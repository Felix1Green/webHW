

def simple_app(environ, start_response):
    print("Привет мир")
    parameters_list = [(i,value) for i,value in environ.items()]
    print(parameters_list)
    status = '200 OK'
    output = b'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return output
    # for i,value in request.GET.items:
    #     parameters_list.append((i,value))
    # for i, value in request.POST.items:
    #     parameters_list.append((i, value))
    #
    # print(parameters_list)


application = simple_app


