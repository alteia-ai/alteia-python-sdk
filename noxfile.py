import functools
import os
import shutil
from pathlib import Path

import nox

PYTHON_VERSION = "3.11"
MODULE = "alteia"
PROJECT_DIR = Path(__file__).parent
REQS_DIR = PROJECT_DIR / "requirements"
REPORT_DIR = PROJECT_DIR / "reports"
COV_DIR = REPORT_DIR / "coverage"
LINT_DIR = REPORT_DIR / "lint"
OPENAPI_DIR = PROJECT_DIR / "static" / "openapi.yaml"
EPHEMERAL_USER_MAIL = os.getenv("EPHEMERAL_USER_MAIL")

nox.options.sessions = ["format", "lint", "tests", "precommit"]
nox.options.reuse_existing_virtualenvs = True  # False to recreate the env


def ensure_deps(groups_name):  # type: ignore
    def decorator(f):  # type: ignore
        @functools.wraps(f)
        def wrapper_debug(session, *args, **kwargs):  # type: ignore
            session.run("poetry", "install", "--with", ",".join(groups_name), external=True)

            return f(session, *args, **kwargs)

        return wrapper_debug

    return decorator


@nox.session(python=PYTHON_VERSION)
@ensure_deps(groups_name=["format"])
def format(session):
    session.run("ruff", "check", "--select", "I", "--fix")
    session.run("ruff", "format", MODULE)


@nox.session(python=PYTHON_VERSION)
@ensure_deps(groups_name=["format"])
def format_check(session):
    """
    For CI, only check if something would be modified
    """
    session.run("ruff", "check", "--select", "I")
    session.run("ruff", "format", MODULE, "--check")


@nox.session(python=PYTHON_VERSION)
@ensure_deps(groups_name=["lint"])
def lint(session: nox.Session) -> None:
    # Start ruff
    session.run(
        "ruff",
        "check",
        MODULE,
    )

    session.run("mypy", MODULE)


@nox.session(python=["3.11", "3.12", "3.13"])
@ensure_deps(groups_name=["tests"])
def tests(session):
    shutil.rmtree(COV_DIR, ignore_errors=True)
    os.makedirs(COV_DIR, exist_ok=True)

    session.run(
        "coverage",
        "run",
        "--source",
        MODULE,
        "-m",
        "pytest",
        "--junitxml=result.xml",
    )

    session.run(
        "coverage",
        "html",
        "-d",
        f"{COV_DIR}",
        "--skip-empty",
        success_codes=[0, 2],
    )

    session.run("coverage", "report")


@nox.session(python=PYTHON_VERSION)
@ensure_deps(groups_name=["pre-commit"])
def precommit(session):
    session.run("pre-commit", "--version")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "--all-files")
