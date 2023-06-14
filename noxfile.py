import laminci
import nox

nox.options.default_venv_backend = "none"


@nox.session
def lint(session: nox.Session) -> None:
    laminci.nox.run_pre_commit(session)


@nox.session
def build(session):
    session.install(".[dev,test]")
    laminci.nox.run_pytest(session)
    laminci.nox.build_docs(session)
