from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from screendoor.models import Position, Applicant


# Sets the applicant filter session variable
@login_required(login_url='login', redirect_field_name=None)
def filter_applicants(request, reference, position_id, applicant_filter):
    request.session['applicant_filter'] = applicant_filter
    return redirect('position', reference=reference, position_id=position_id)


# Sets the applicant sort session variable
@login_required(login_url='login', redirect_field_name=None)
def sort_applicants(request, reference, position_id, sort_by):
    request.session['applicants_sort'] = sort_by
    return redirect('position', reference=reference, position_id=position_id)


# Sets the position sort session variable
@login_required(login_url='login', redirect_field_name=None)
def sort_positions(request, sort_by):
    # Persists positions sorting
    request.session['position_sort'] = sort_by
    return redirect('positions')


# Gets user's persisted positions sort method, or returns default
def get_positions_sort_method(request):
    try:
        return request.session['position_sort']
    except KeyError:
        return '-created'


# Gets user's persisted applicants sort method, or returns default
def get_applicants_sort_method(request):
    try:
        return request.session['applicants_sort']
    except KeyError:
        return '-percentage_correct'


# Gets the user's persisted applicant filter method, or returns default
def get_applicant_filter_method(request):
    try:
        return request.session['applicant_filter']
    except KeyError:
        return "all"


# Return whether the position exists and the user has access to it
def user_has_position(request, reference, position_id):
    if Position.objects.filter(reference_number=reference).exists(
    ) and request.user.positions.filter(reference_number=reference).exists():
        return Position.objects.get(id=position_id)
    return None


# Combines applicants with whether they are favourited or not
def create_applicants_wth_favourite_information(applicants, favourites):
    stitched_lists = {}
    for applicant in applicants:
        if applicant in favourites:
            stitched_lists[applicant] = True
        else:
            stitched_lists[applicant] = False
    return stitched_lists


# Verify that the applicant exists and belongs to position that user has access to
def position_has_applicant(request, app_id):
    if Applicant.objects.filter(
            applicant_id=app_id).exists() and user_has_position(
                request,
                Applicant.objects.get(
                    applicant_id=app_id).parent_position.reference_number,
                Applicant.objects.get(applicant_id=app_id).parent_position.id):
        return Applicant.objects.get(applicant_id=app_id)
