#_*_ coding: utf-8 _*_

import sys
import traceback

def tryexcept(out_sys, default_ret, warn_message, warn_form_func):
    def tryexcept_decorator(f):
        def new_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
        
            except:
                if not warn_message:
                    #warn_message = traceback.format_exc() # 内层函数可以访问外层函数中定义的变量,但不能重新赋值(rebind)
                    msg = traceback.format_exc().replace('\n', '\\n')
                else:
                    msg = warn_message
                if warn_form_func:
                    msg = warn_form_func(msg)
                out_sys.write(msg)
                return default_ret
            
        new_f.func_name = f.func_name
        return new_f
    return tryexcept_decorator


def usual_warn_form(msg):
    import datetime
    return "[%s]%s" % (str(datetime.datetime.now()), msg)

usualtryexcept = tryexcept(out_sys=sys.stdout, default_ret=None, warn_message=None, warn_form_func=usual_warn_form)



def accepts(*types):
    def check_accepts(f):
        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a,t)
            return f(*args, **kwds)
        new_f.func_name = f.func_name
        return new_f
    return check_accepts

def returns(rtype):
    def check_returns(f):
        def new_f(*args, **kwds):
            result = f(*args, **kwds)
            assert isinstance(result, rtype), \
                   "return value %r does not match %s" % (result,rtype)
            return result
        new_f.func_name = f.func_name
        return new_f
    return check_returns

