#! /usr/bin/python

import sys

sys.path.append('../lib')
sys.path.append('../conf')

import web
import v1

urls = (
    '/v1/gate_machine/get_schedules(/?|/.*)', v1.app.schedule,
    '/v1/gate_machine/update_time(/?|/.*)', v1.app.update_time,
    '/v1/gate_machine/exit_authen(/?|/.*)', v1.app.exit_authen,
    '/v1/gate_machine/leave(/?|/.*)', v1.app.leave,
    '/v1/gate_machine/get_privilege(/?|/.*)', v1.app.get_privilege,
    '/v1/gate_machine/set_privilege(/?|/.*)', v1.app.set_privilege,
    '/v1/gate_machine/get_room_info(/?|/.*)', v1.app.get_room_info,
    '/v1/gate_machine/admittance(/?|/.*)', v1.app.admittance,
    '/v1/gate_machine/reprint(/?|/.*)', v1.app.reprint,
    '/v1/gate_machine/enter_authen(/?|/.*)', v1.app.enter_authen,
    '/v1/gate_machine/set_room_info(/?|/.*)', v1.app.set_room_info,
    '/v1/gate_machine/advertise(/?|/.*)', v1.app.advertise,
    '/v1/gate_machine/ticket_usage(/?|/.*)', v1.app.TicketUsage
)

app = web.application(urls, globals())

def notfound():
    return web.notfound("Invalid uri!")

app.notfound = notfound

def internalerror():
    return web.internalerror("Some inner exception occurred!")

app.internalerror = internalerror

def proc(handle):
    # print "-- In proc() : Beginning ..."

    ret = handle()

    try:
        pass
        # print "--- In proc()"
        # 1 / 0
    except:
        # print('Uh oh')
        pass
    return ret

app.add_processor(proc)

if __name__ == "__main__":
    web.config.debug = False
    app.run()
