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
    Depends
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Annotated, List
from contextlib import asynccontextmanager
from random import randint
from dataclasses import dataclass
from schemas import PersonCreateSchema, PersonResponseSchema, PersonUpdateSchema
from database import Base, engine, Person, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up...")
    # Base.metadata.create_all(engine)
    yield
    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)


"""
names_list = [
    {"id": 1, "name": "jack"},
    {"id": 2, "name": "max"},
    {"id": 3, "name": "mika"},
    {"id": 4, "name": "david"},
    {"id": 5, "name": "peter"},
]
"""


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


@app.get("/names", response_model=list[PersonResponseSchema])
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
    db: Session = Depends(get_db)
):

    query = db.query(Person)
    if q:
        query = query.filter_by(name=q)
    
    result = query.all()
    return result


"""
@app.get("/names", response_model=list[PersonResponseSchema])
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
"""


@app.post(
    "/names", response_model=PersonResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_name(request: PersonCreateSchema, db: Session = Depends(get_db)):
    new_person = Person(name=request.name)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person


"""
@app.post(
    "/names", response_model=PersonResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_name(person: PersonCreateSchema):
    name_obj = {"id": randint(6, 100), "name": person.name}
    names_list.append(name_obj)
    return name_obj
"""


"""
@dataclass
class Student:
    name: str
    age: int


@dataclass
class StudentResponse:
    id: int
    name: str
    age: int


@app.post("/names", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_name(student: Student):
    name_obj = {"id": randint(6, 100), "name": student.name, "age": student.age}
    names_list.append(name_obj)
    return name_obj
"""


"""
@app.post("/names", status_code=status.HTTP_201_CREATED)
def create_name(name: str = Body(embed=True)):
    name_obj = {"id": randint(6, 100), "name": name}
    names_list.append(name_obj)
    return name_obj
"""

@app.get("/names/{person_id}", response_model=PersonResponseSchema)
def retrieve_name_detail(
    person_id: Annotated[
        int,
        Path(
            title="Person ID",
            description="The ID of the Person to retrieve.",
        ),
    ],
    db: Session = Depends(get_db)
):

    person = db.query(Person).filter_by(id=person_id).one_or_none()

    if person:
        return person
    else:    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="person not found!"
        )


"""
@app.get("/names/{name_id}", response_model=PersonResponseSchema)
def retrieve_name_detail(
    name_id: Annotated[
        int,
        Path(
            title="Object ID",
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
"""


@app.put(
    "/names/{name_id}",
    response_model=PersonResponseSchema,
    status_code=status.HTTP_200_OK,
)
def update_name_detail(request: PersonUpdateSchema, name_id: int = Path(), db: Session = Depends(get_db)):
    person = db.query(Person).filter_by(id=name_id).one_or_none()
    if person:
        person.name = request.name
        db.commit()
        db.refresh(person)
        return person
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
        )


"""
@app.put(
    "/names/{name_id}",
    response_model=PersonResponseSchema,
    status_code=status.HTTP_200_OK,
)
def update_name_detail(person: PersonUpdateSchema, name_id: int = Path()):
    for item in names_list:
        if item["id"] == name_id:
            item["name"] = person.name
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
    )
"""


"""
@app.put("/names/{name_id}", status_code=status.HTTP_200_OK)
def update_name_detail(name_id: int = Path(), name: str = Form()):
    for item in names_list:
        if item["id"] == name_id:
            item["name"] = name
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
    )
"""


@app.delete("/names/{name_id}")
def delete_name(name_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter_by(id=name_id).one_or_none()
    if person:
        db.delete(person)
        db.commit()
        return JSONResponse(
            content={"detail": "object removed successfully!"},
            status_code=status.HTTP_200_OK,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="object not found!"
        )


"""
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
"""


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
