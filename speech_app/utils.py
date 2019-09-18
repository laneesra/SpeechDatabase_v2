import argparse
import asyncio
import os
import pathlib

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict

import trafaret as t
from aiohttp import web
from trafaret_config import commandline
from .worker import warm, clean


PATH = pathlib.Path(__file__).parent.parent
settings_file = os.environ.get('SETTINGS_FILE', 'api.dev.yml')
DEFAULT_CONFIG_PATH = PATH / 'config' / settings_file


CONFIG_TRAFARET = t.Dict({
    t.Key('app'): t.Dict({
        t.Key('host'): t.String(),
        t.Key('port'): t.Int[0: 2 ** 16]
    }),
    t.Key('workers'): t.Dict({
        t.Key('max_workers'): t.Int[1:1024],
        t.Key('model_path'): t.String,
    }),
    t.Key('db'): t.Dict({
        t.Key('database'): t.String,
        t.Key('user'): t.String,
        t.Key('password'): t.String,
        t.Key('host'): t.String,
        t.Key('port'): t.String,
    }),
})


@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int


@dataclass(frozen=True)
class WorkersConfig:
    max_workers: int
    model_path: str

@dataclass(frozen=True)
class DbConfig:
    database: str
    user: str
    password: str
    host: str
    port: str

@dataclass(frozen=True)
class Config:
    app: AppConfig
    workers: WorkersConfig
    db: DbConfig


def config_from_dict(d: Dict[str, Any]) -> Config:
    app_config = AppConfig(  # type: ignore
        host=d['app']['host'],
        port=d['app']['port'])
    workers_config = WorkersConfig(  # type: ignore
        max_workers=d['workers']['max_workers'],
        model_path=d['workers']['model_path'],
    )
    pg_config = DbConfig(
        database=d['db']['database'],
        user=d['db']['user'],
        password=d['db']['password'],
        host=d['db']['host'],
        port=d['db']['port'],
    )
    return Config(app=app_config, workers=workers_config, db=pg_config)  # type: ignore


def get_config(argv: Any = None) -> Config:
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap, default_config=DEFAULT_CONFIG_PATH
    )
    options = ap.parse_args(argv)
    d = commandline.config_from_options(options, CONFIG_TRAFARET)
    return config_from_dict(d)


def init_config(app: web.Application, config: Config) -> None:
    app['config'] = config


async def init_workers(
    app: web.Application, conf: WorkersConfig, conf_db: DbConfig
) -> ProcessPoolExecutor:
    n = conf.max_workers
    executor = ProcessPoolExecutor(max_workers=n)
    path = str(PATH / conf.model_path)
    loop = asyncio.get_event_loop()
    run = loop.run_in_executor
    fs = [run(executor, warm, path, conf_db) for i in range(0, n)]
    await asyncio.gather(*fs)

    async def close_executor(app: web.Application) -> None:
        fs = [run(executor, clean) for i in range(0, n)]
        await asyncio.shield(asyncio.gather(*fs))
        executor.shutdown(wait=True)

    app.on_cleanup.append(close_executor)
    app['executor'] = executor
    return executor