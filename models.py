import os.path as op
from peewee import (SqliteDatabase, Model, CharField, IntegerField,
    ForeignKeyField)


HERE = op.abspath(op.dirname(__file__))
db = SqliteDatabase(op.join(HERE, 'database.db'), threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    name = CharField()

    def __unicode__(self):
        return self.name


class Player(BaseModel):
    group = ForeignKeyField(Group, related_name='players')
    name = CharField()
    order = IntegerField()

    def __unicode__(self):
        return "%s, %d" % (self.name, self.order)


class Puzzle(BaseModel):
    name = CharField()

    def __unicode__(self):
        return self.name


class Answer(BaseModel):
    puzzle = ForeignKeyField(Puzzle, related_name='answers')
    player = ForeignKeyField(Player)
    question = CharField()
    value = CharField()

    def __unicode__(self):
        return '%s - %s - %s - %s' % (
            self.puzzle, self.player, self.question, self.value)
