import ssl
from celery import Celery


app = Celery(
    'CELERY_WEB',
    broker='amqps://eajtisqv:SJRh_GntJcqx1wUXz3Wqq4F0H9DQv6UN@hawk.rmq.cloudamqp.com/eajtisqv//',
    backend='rpc://',
    include=['commenta.tasks']
)#celery -A commenta.worker worker --loglevel=INFO 
#export PATH=$PATH:/usr/local/sbin

#celery flower -A commenta.worker --broker:amqps://eajtisqv:SJRh_GntJcqx1wUXz3Wqq4F0H9DQv6UN@hawk.rmq.cloudamqp.com/eajtisqv
#celery flower -A commenta.worker --broker:pyamqp://guest@localhost
#celery flower -A commenta.worker --broker:amqp://guest@localhost