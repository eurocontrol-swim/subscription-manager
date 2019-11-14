"""
Copyright 2019 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the 
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following 
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products 
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative:
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""
import enum
from datetime import datetime, timezone

from swim_backend.db import db

__author__ = "EUROCONTROL (SWIM)"


def created_at_default(context):
    params = context.get_current_parameters()
    if not params['created_at']:
        return datetime.now(timezone.utc)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=created_at_default)
    active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


topic_subscriptions_table = db.Table(
    'topic_subscriptions', db.Model.metadata,
    db.Column('topic_id', db.Integer, db.ForeignKey('topics.id')),
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscriptions.id'))
)


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    user = db.relationship("User", backref='topics')
    subscriptions = db.relationship("Subscription",
                                    secondary=topic_subscriptions_table,
                                    backref="topics")


class QOS(enum.Enum):
    AT_LEAST_ONCE = "AT_LEAST_ONCE"
    AT_MOST_ONCE = "AT_MOST_ONCE"
    EXACTLY_ONCE = "EXACTLY_ONCE"

    @classmethod
    def all(cls):
        return [e.value for e in cls]


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    queue = db.Column(db.String(128), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    qos = db.Column(db.Enum(QOS), nullable=False, default=QOS.EXACTLY_ONCE.value)
    durable = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", backref='subscriptions')

    @property
    def topic_names(self):
        return [topic.name for topic in self.topics]
