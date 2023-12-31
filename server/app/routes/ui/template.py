from jinja2 import PackageLoader, select_autoescape
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    loader=PackageLoader("app"), autoescape=select_autoescape(), directory="dummy"
)
