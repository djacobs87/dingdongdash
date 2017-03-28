from django.http import HttpResponse

import core.functions as ddd


def process_button(request):
    if(request.method != "POST"):
        return HttpResponse("Method not allowed", status=400)

    spoof = request.POST.get('spoof', False)

    try:
        result = ddd.process_button(
            battery_voltage=request.POST.get('batteryVoltage'),
            serial_number=request.POST.get('serialNumber'),
            click_type=request.POST.get('clickType'),
            spoof=spoof
        )

        if hasattr(result, 'rider'):
            return HttpResponse(result.rider, status=207)

        return HttpResponse('Success')
    except Exception as e:
        return HttpResponse(e, status=400)
