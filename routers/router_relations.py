from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from classes.database import get_cursor
from classes import models_orm
import utilities
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
from pydantic.typing import Annotated
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

# router
router= APIRouter(
    prefix="/relations",
    tags=["Relations"]
)
# API endpoint to retrieve all relationships between students and classes
@router.get('')
async def list_relations(cursor: Session = Depends(get_cursor)):
    # Get all relations between students and classes
    all_relations = cursor.query(models_orm.student_class_association).all()
    # Convert relations to dictionaries
    relations_dict = [
        {
            'student_id': relation.student_id,
            'class_id': relation.class_id,
            'created_at': relation.created_at
        }
        for relation in all_relations
    ]
    return jsonable_encoder(relations_dict)

class Relation_post(BaseModel):
    student_id:int
    class_id:int

# API endpoint to link a student with a class
@router.post('', status_code=status.HTTP_201_CREATED)
async def create_relation(payload: Relation_post, cursor: Session = Depends(get_cursor)):
    new_relation = models_orm.student_class_association.insert().values(student_id=payload.student_id, class_id=payload.class_id)
    try:
        cursor.execute(new_relation)
        cursor.commit()
        return {'message': 'New relation was added successfully'}
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error while creating relation between student and class'
        )