from django.http import HttpResponse


def equipment_list(request):
    return HttpResponse("Listado de equipos")


def equipment_detail(request, pk):
    return HttpResponse(f"Detalle del equipo {pk}")


def equipment_create(request):
    return HttpResponse("Crear equipo")


def equipment_update(request, pk):
    return HttpResponse(f"Editar equipo {pk}")


def equipment_retire(request, pk):
    return HttpResponse(f"Retirar equipo {pk}")
