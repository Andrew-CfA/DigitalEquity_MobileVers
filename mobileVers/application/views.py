from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserForm, AddressForm, EligibilityForm, programForm, zipCodeForm,futureEmailsForm
from .backend import addressCheck, validateUSPS, qualification
from django.http import QueryDict

import logging


formPageNum = 6

# first index page we come into
def index(request):

    foco_zipCodes = [80521, 80523, 80525, 80527, 80522, 80524, 80526, 80528, 80553]

    if request.method == "POST": 
        form = zipCodeForm(request.POST or None)
        if form.is_valid():
            try:
                form.save()
                if form.cleaned_data['zipCode'] in foco_zipCodes:
                    return redirect(reverse("application:available"))
                else:
                    return redirect(reverse("application:notAvailable"))
            except AttributeError:
                #TODO implement look into logs!
                logging.warning("insert valid zipcode")
    
    form = zipCodeForm()
    logout(request)
    return render(request, 'application/index.html', {
            'form':form,
        })

def address(request):
    foco_zipCodes = [80521, 80523, 80525, 80527, 80522, 80524, 80526, 80528, 80553] #TODO implement this for zipcode fail function if client inputs zip outside of FoCo
    if request.method == "POST": 
        try:
            existing = request.user.addresses
            form = AddressForm(request.POST,instance = existing)
        except ObjectDoesNotExist:
            form = AddressForm(request.POST or None)

        print(form.data)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_id = request.user
            for zipCode in foco_zipCodes:
                print(instance.zipCode)
                print(zipCode)
                if instance.zipCode == zipCode:
                    print("breaking for some reason...")
                    break
            else:
                print("address not found")
                return redirect(reverse("application:notInRegion"))
            addressResult = addressCheck(instance.address.upper())
            if addressResult == True:
                instance.n2n = True
                print("n2n instance is true")
            else:
                instance.n2n = False
                print("n2n instance is false")
            instance.save()            
            return redirect(reverse("application:addressCorrection"))
    else:
        form = AddressForm()

    return render(request, 'application/address.html', {
        'form':form,
        'step':2,
        'request.user':request.user,
        'formPageNum':formPageNum,
        })


def addressCorrection(request):
    try:
        q = QueryDict('', mutable=True)
        q.update({"address": request.user.addresses.address, 
            "address2": request.user.addresses.address2, 
            "city": request.user.addresses.city,
            "state": request.user.addresses.state,
            "zipcode": str(request.user.addresses.zipCode),})
        dict_address = validateUSPS(q)
        print(dict_address['AddressValidateResponse']['Address'])
        program_string_2 = [dict_address['AddressValidateResponse']['Address']['Address2'], 
                            dict_address['AddressValidateResponse']['Address']['Address1'],
                            dict_address['AddressValidateResponse']['Address']['City'] + " "+ dict_address['AddressValidateResponse']['Address']['State'] +" "+  str(dict_address['AddressValidateResponse']['Address']['Zip5'])]
    except TypeError or RelatedObjectDoesNotExist:
        program_string_2 = ["Sorry, we couldn't verify this address through USPS."]
        print("USPS couldn't figure it out!")
    program_string = [request.user.addresses.address, request.user.addresses.address2, request.user.addresses.city + " " + request.user.addresses.state + " " + str(request.user.addresses.zipCode)]
    return render(request, 'application/addressCorrection.html',  {
        'step':2,
        'formPageNum':formPageNum,
        'program_string': program_string,
        'program_string_2': program_string_2,
    })

def takeUSPSaddress(request):
    try:
        q = QueryDict('', mutable=True)
        q.update({"address": request.user.addresses.address, 
            "address2": request.user.addresses.address2, 
            "city": request.user.addresses.city,
            "state": request.user.addresses.state,
            "zipcode": str(request.user.addresses.zipCode),})
        dict_address = validateUSPS(q)

        instance = request.user.addresses
        instance.user_id = request.user
        instance.address = dict_address['AddressValidateResponse']['Address']['Address2']
        addressResult = addressCheck(instance.address)
        if addressResult == True:
            instance.n2n = True
            print("n2n instance is true")
        else:
            instance.n2n = False
            print("n2n instance is false")

        instance.address2 = dict_address['AddressValidateResponse']['Address']['Address1']
        instance.city = dict_address['AddressValidateResponse']['Address']['City']
        instance.state = dict_address['AddressValidateResponse']['Address']['State']
        instance.zipCode = int(dict_address['AddressValidateResponse']['Address']['Zip5'])

        instance.save()
    except TypeError or RelatedObjectDoesNotExist:
        print("USPS couldn't figure it out!")

    return redirect(reverse("application:n2n"))



def n2n(request):
    if request.user.addresses.n2n == True:
        return redirect(reverse("application:finances")) #TODO figure out to clean?
    else:
        return redirect(reverse("application:finances")) 


def account(request):
    if request.method == "POST": 
        # maybe also do some password requirements here too
        try:
            existing = request.user
            form = UserForm(request.POST,instance = existing)
        except AttributeError or ObjectDoesNotExist:
            form = UserForm(request.POST or None)
        if form.is_valid():
            # Add Error MESSAGE IF THEY DIDN"T WRITE CORRECT THINGS TO SUBMIT
            # Make sure password isn't getting saved twice
            print(form.data)
            try:
                user = form.save()
                login(request,user)
                print("userloggedin")
            except AttributeError:
                print("user error, login not saved, user is: " + str(user))
            return redirect(reverse("application:address"))
    else:
        form = UserForm()

    return render(request, 'application/account.html', {
    'form':form,
    'step':1,
    'formPageNum':formPageNum,
    })
#    else:
#        return redirect(reverse(page))


def finances(request):
    if request.method == "POST":
        try:
            existing = request.user.eligibility
            form = EligibilityForm(request.POST,instance = existing)
        except AttributeError or ObjectDoesNotExist:
            form = EligibilityForm(request.POST or None)
        if form.is_valid():
            print(form.data)
            instance = form.save(commit=False)
            instance.user_id = request.user       
            #take dependent information, compare that AMI level number with the client's income selection and determine if qualified or not, flag this
            if form['grossAnnualHouseholdIncome'].value() == 'Below $19,800':
                print("GAHI is below 19,800")
                if qualification(form['dependents'].value(),) >= 19800:
                    instance.DEqualified = True
                else:
                    instance.DEqualified = False
            elif form['grossAnnualHouseholdIncome'].value() == '$19,800 ~ $32,800':
                print("GAHI is between 19,800 and 32,800")
                if 19800 <= qualification(form['dependents'].value(),) <= 32800:
                    instance.DEqualified = True
                else:
                    instance.DEqualified = False
            elif form['grossAnnualHouseholdIncome'].value() == 'Over $32,800':
                print("GAHI is above 32,800")
                if qualification(form['dependents'].value(),) >= 32800:
                    instance.DEqualified = True
                else:
                    instance.DEqualified = False                        
                
            print("SAVING")
            instance.save()
            if instance.DEqualified == True:
                return redirect(reverse("application:mayQualify"))
            else:
                return redirect(reverse("application:programs"))
        else:
            print(form.data)
    else:
        form = EligibilityForm()

    return render(request, 'application/finances.html', {
        'form':form,
        'step':3,
        'formPageNum':formPageNum,
    })


def GRQuickApply(request):
    obj = request.user.eligibility
    print(obj.GRqualified)
    #print(request.user.eligibility.GRQualified)
    obj.GRqualified = True
    print(obj.GRqualified)
    obj.save()
    return render(request, "application/GRQuickApply.html",)

def RecreationQuickApply(request):
    obj = request.user.eligibility
    print(obj.RecreationQualified)
    #print(request.user.eligibility.GRQualified)
    obj.RecreationQualified = True
    print(obj.RecreationQualified)
    obj.save()
    return render(request, "application/RecreationQuickApply.html",)


def programs(request):
    if request.method == "POST": 
        try:
            existing = request.user.programs
            form = programForm(request.POST,instance = existing)
        except AttributeError or ObjectDoesNotExist:
            form = programForm(request.POST or None)
        if form.is_valid():
            print(form.data)
            print(request.session)
            try:
                instance = form.save(commit=False)
                instance.user_id = request.user
                instance.save()
                return redirect(reverse("dashboard:files"))
            except IntegrityError:
                print("User already has information filled out for this section")
            #enter upload code here for client to upload images
            return redirect(reverse("application:available"))
    else:
        form = programForm()

    return render(request, 'application/programs.html', {
    'form':form,
    'step':4,
    'formPageNum':formPageNum,
    })

#    else:
#        return redirect(reverse(page))
    #return render(request, 'application/programs.html',)












def available(request):
    return render(request, 'application/de_available.html',)

def notInRegion(request):
    return render(request, 'application/notInRegion.html',)

def privacyPolicy(request):
    return render(request, 'application/privacyPolicy.html',)

def dependentInfo(request):
    return render(request, 'application/dependentInfo.html',)


def notAvailable(request):
    
    if request.method == "POST": 
        form = futureEmailsForm(request.POST or None)
        if form.is_valid():
            try:
                form.save()
                return redirect(reverse("application:index"))
            except AttributeError:
                print("Error Email Saving")
    
    form = futureEmailsForm()
    return render(request, 'application/de_notavailable.html', {
            'form':form,
        })



def mayQualify(request):
    return render(request, 'application/mayQualify.html',{
        'step':3,
        'formPageNum':formPageNum,
    })

