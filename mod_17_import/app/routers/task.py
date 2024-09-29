from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import *
from app.models import User
from app.schemas import CreateUser, UpdateUser, CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    tsk = db.scalars(select(Task).where(Task.id == task_id))
    if tsk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого пользователя не найдено'
        )
    else:
        return tsk


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], usr_id: int, create_tsk: CreateTask):
    usr = db.scalars(select(User).where(User.id == usr_id))
    if usr is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого пользователя не найдено'
        )
    else:
        db.execute(insert(Task).values(title=create_tsk.title,
                                       content=create_tsk.content,
                                       priority=create_tsk.priority,
                                       user_id=usr_id,
                                       slug=slugify(create_tsk.title))
                   )
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Задача создана'
        }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], tsk_id: int, update_tsk: UpdateTask):
    tsk = db.scalar(select(Task).where(Task.id == tsk_id))
    if tsk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такой задачи не найдено'
        )
    db.execute(update(Task).where(Task.id == tsk_id).values(
        title=update_tsk.title,
        content=update_tsk.content,
        priority=update_tsk.priority)
    )
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Задача обновлена'
    }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], tsk_id: int):
    tsk = db.scalar(select(Task).where(Task.id == tsk_id))
    if tsk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такой задачи не найдено'
        )
    db.execute(delete(Task).where(Task.id == tsk_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Задача удалена'
    }
