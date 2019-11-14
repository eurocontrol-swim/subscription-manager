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
from swim_backend.db import db
from subscription_manager.broker import broker
from swim_backend.events import EventHandler

__author__ = "EUROCONTROL (SWIM)"


class UpdateSubscription(EventHandler):

    def __init__(self, current_subscription, updated_subscription):
        self.current_subscription = current_subscription
        self.updated_subscription = updated_subscription

    def do(self, *args, **kwargs): pass
    def undo(self, *args, **kwargs): pass


class DbUpdateSubscription(UpdateSubscription):
    def do(self, *args, **kwargs):
        db.update_subscription(self.updated_subscription)

    def undo(self, *args, **kwargs):
        db.update_subscription(self.current_subscription)


class BrokerUpdateSubscription(UpdateSubscription):
    @staticmethod
    def _perform_update(current_subscription, updated_subscription):
        if current_subscription.active != updated_subscription.active:
            if not updated_subscription.active:
                for topic_name in updated_subscription.topic_names:
                    broker.delete_queue_binding(queue=updated_subscription.queue,
                                                topic=topic_name)
            else:
                for topic_name in updated_subscription.topic_names:
                    broker.bind_queue_to_topic(queue=updated_subscription.queue,
                                               topic=topic_name,
                                               durable=updated_subscription.durable)

    def do(self, *args, **kwargs):
        self._perform_update(current_subscription=self.current_subscription,
                             updated_subscription=self.updated_subscription)

    def undo(self, *args, **kwargs):
        self._perform_update(current_subscription=self.updated_subscription,
                             updated_subscription=self.current_subscription)
