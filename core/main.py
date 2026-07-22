from fastapi import (
    FastAPI,
    status,
    HTTPException,
    Path,
    Query,
    Form,
    Body,
    File,
    UploadFile,
)
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, List
from contextlib import asynccontextmanager
from random import randint


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up...")
    yield
    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)

names_list = [
    {"id": 1, "name": "Jack"},
    {"id": 2, "name": "Max"},
    {"id": 3, "name": "Mika"},
    {"id": 4, "name": "David"},
    {"id": 5, "name": "Peter"},
]


""" The on_event method is deprecated
@app.on_event("startup")
async def startup_event():
    print("starting the application...")


@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down the application...")
"""


@app.get("/")
def root():
    content = {"message": "Hello World!"}
    return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)


@app.get("/names")
def retrieve_names_list(
    q: Annotated[
        str | None,
        Query(
            alias="search",
            description="Filter names by the provided search term.",
            # example="John",
            max_length=50,
        ),
    ] = None,
):
    # def retrieve_names_list(q: str | None = Query(default=None, max_length=50)):
    # def retrieve_names_list(q: Optional[str] = None):
    # def retrieve_names_list(q: str | None = None):
    if q:
        return [item for item in names_list if item["name"] == q]
    return names_list


@app.post("/names", status_code=status.HTTP_201_CREATED)
def create_name(name: str = Body(embed=True)):
    name_obj = {"id": randint(6, 100), "name": name}
    names_list.append(name_obj)
    return name_obj


@app.get("/names/{name_id}")
def retrieve_name_detail(
    name_id: Annotated[
        int,
        Path(
            alias="object_id",
            title="object id",
            description="The ID of the name to retrieve.",
        ),
    ],
):
    for name in names_list:
        if name["id"] == name_id:
            return name
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
    )


@app.put("/names/{name_id}", status_code=status.HTTP_200_OK)
def update_name_detail(name_id: int = Path(), name: str = Form()):
    for item in names_list:
        if item["id"] == name_id:
            item["name"] = name
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
    )


@app.delete("/names/{name_id}")
def delete_name(name_id: int):
    for item in names_list:
        if item["id"] == name_id:
            names_list.remove(item)
            return JSONResponse(
                content={"detail": "object removed successfully!"},
                status_code=status.HTTP_200_OK,
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
    )


@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # print(file.__dict__)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(content),
    }


@app.post("/upload-multiple/")
async def upload_multiple(files: List[UploadFile]):
    return [
        {"filename": file.filename, "content_type": file.content_type} for file in files
    ]


# @app.post("/upload_file/")
# async def upload_file(file: bytes = File(...)):
#     print(file)
#     return {"file_size": len(file)}
