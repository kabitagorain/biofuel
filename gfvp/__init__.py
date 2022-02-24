def null_session(request):
    if 'interested_in' in request.session:
        request.session['interested_in'] = ''   
    if request.user.is_authenticated:
            try:
                del request.session['interested_in']
            except:
                pass