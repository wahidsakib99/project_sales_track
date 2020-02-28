'''
Necessary library files import
'''
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core import validators
from django.db.models import Sum
import datetime
import calendar
import json
from django.utils import timezone
import operator
from collections import OrderedDict
# database collections
from .models import user_info
from .models import device_info
from .models import sales_track

# import for ML
from sklearn.linear_model import LinearRegression
import numpy as np

'''
Session kept in session['user_id] => user_id
'''

'''
register_page => checks for the session. for sessions it redirects user to 'Dashboard'.
                 else it redirects user to register page
'''
def register_page(request):
    try:
        if request.session['user_id']:
            return redirect('Dashboard')
    except:
        return render(request,'project_sales_track/register.html')

'''
verify_register => It takes input from register_page. No need to verify these data. It has been done via ajax.
                   Saves data into mongoDB.
'''
def verify_register(request):
    try:
        '''
        Receives input from register page
        '''
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        device_label = request.POST.get('device_label')
        device_id = request.POST.get('device_id')
        ppkg = float(request.POST.get('ppkg'))
        store_name = request.POST.get('store_name')
        ''''
        Saves data into user_info collections
        '''
        user_info(name = name,email = email,password = password,store_name = store_name).save()

        '''
        update device_label and pp_kg of device_info collections
        '''
        device_info.objects.filter(device_id = device_id).update(device_label = device_label,pp_kg = ppkg,user_id = user_info.objects.get(email = email))

        '''
        insert data into device_under_user
        '''
        #device_under_user(user_id = user_info.objects.get(email = email) ,device_id = device_info.objects.get(device_id = device_id)).save()

        return redirect('return_login_page')
    except Exception as e:
        return HttpResponse(e)

def return_login_page(request):
    '''
    If session has user_id redirect them to dashboard page
    else redirect to login page
    '''
    try:
        if request.session['user_id']:
            return redirect('Dashboard')
    except:
        return render(request,'project_sales_track/login.html',{'status':True})

def verify_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            x = user_info.objects.get(email=email,password=password)
            if x:
                request.session['user_id'] = x.id
                return redirect('Dashboard')
                # return HttpResponse(x.name)
            else:
                raise # raise exception
        except:
            # messages.add_message(request,messages.error,"Username or Password didn't match.")
            return redirect('return_login_page')


'''
Dashboard for users
'''
def dashboard(request):
    today = timezone.now()
    try:
        if request.session['user_id']:
            user_data = user_info.objects.get(id = request.session['user_id'])
            devices = device_info.objects.filter(user_id_id = user_data)

            '''
            Collect data before 4 months
            calculate total sales
            '''
            four_months_date = datetime.date.today() - datetime.timedelta(4*365/12)
            total_sale = 0
            for i in range(len(devices)):
                x = sales_track.objects.filter(device_id_id = devices[i].id,date_created__range = (four_months_date, datetime.datetime.now())).aggregate(Sum('sales'))['sales__sum']
                if x == None:
                    x = 0

                y = device_info.objects.get(id = devices[i].id).pp_kg
                total_sale += x * y

            '''
            Total kg sold today
            '''
            #total_sold_today_kg = sum(sales_track.objects.filter(device_id_id__in = [p.id for p in devices], date_created = datetime.date.today()))
            total_sold_today_kg = 0
            for i in range(len(devices)):
                x = sales_track.objects.filter(device_id_id = devices[i].id, date_created__range = (datetime.date(today.year,today.month,today.day), datetime.date(today.year,today.month,today.day + 1))).aggregate(Sum('sales'))['sales__sum']
                if x == None:
                    x = 0
                total_sold_today_kg += x
            
            '''
            Sold today in taka
            '''
            kgs_today = sales_track.objects.filter(device_id_id__in = [p.id for p in devices], date_created__range = (datetime.date(today.year,today.month,today.day), datetime.date(today.year,today.month,today.day + 1)) )
            total_sale_today_taka = 0
            for each_device in devices:
                for each_kg in kgs_today:
                    if each_kg.device_id_id == each_device.id:
                        total_sale_today_taka += each_kg.sales * each_device.pp_kg
            
            '''
            TOP SELLING DEVICE DATA of TODAY
            '''
            x = {}
            for each_device in devices:
                l = sales_track.objects.filter(device_id_id = each_device.id,date_created__range = (datetime.date(today.year,today.month,today.day), datetime.date(today.year,today.month,today.day + 1))).aggregate(Sum('sales'))['sales__sum']
                if l == None:
                    l = 0
                x[each_device.device_label] = l
            '''
            Top selling data of four months
            '''
            y = {}
            for each_device in devices:
                l = sales_track.objects.filter(device_id_id = each_device.id,date_created__range = (four_months_date, timezone.now())).aggregate(Sum('sales'))['sales__sum']
                if l == None:
                    l = 0
                y[each_device.device_label] = l

            sorted(x.items(),key=operator.itemgetter(1),reverse=True)
            # reversed(sorted(x.values()))
            # reversed(sorted(y.items()))
            # max_x_key = max(x, key=lambda k: x[k])
            # max_x_value = x[max_x_key]
            max_y_key = max(y, key=lambda k: y[k])
            max_y_value = y[max_y_key]
            data = {
                'title' : 'Seller Dashboard',
                'user_data' : user_data,
                'devices' : devices,
                'total_sale' : "{0:.3f}".format(total_sale),
                'sold_today' : "{0:.3f}".format(total_sold_today_kg),
                'sold_today_taka' : "{0:.3f}".format(total_sale_today_taka),
                'date_time' : datetime.date.today(),
                'selling_today' : x,
                'four_month_device' : max_y_key,
                'four_month_value' : max_y_value,
            }
            return render(request,'project_sales_track/dashboard.html',data)
            # return HttpResponse()
    except Exception as e:
        # return redirect('return_login_page')
        return HttpResponse(e)


def seller_data(request):
    try:
        if request.session['user_id']:
            user_data = user_info.objects.get(id = request.session['user_id'])
            devices = device_info.objects.filter(user_id_id = user_data)
            data = {
                'title' : 'Seller Dashboard',
                'user_data' : user_data,
                'devices' : devices,
            }
            return render(request,'project_sales_track/seller_data.html',data)
    except:
        return redirect('return_login_page')

    


def statistics(request):
    try:
        if request.session['user_id']:
            user_data = user_info.objects.get(id = request.session['user_id'])
            devices = device_info.objects.filter(user_id_id = user_data)
            data = {
                'title' : 'Seller Dashboard',
                'user_data' : user_data,
                'devices' : devices,
            }
            return render(request,'project_sales_track/statistics.html',data)
    except Exception as e:
        # return redirect('return_login_page')
        return HttpResponse(e)            

def logout(request):
    try:
        del request.session['user_id']
        return redirect('return_login_page')
    except:
        return HttpResponse("Logout Failed")


'''
Views for ajax
'''
def ajax_return_bar_data(request):
    if request.is_ajax():
        '''
        This function returns data of last four months to javascript to show as bar
        '''
        four_months_name = []
        four_months_number = []
        four_months_year = []
        '''
        Find previous four Months
        '''
        today = datetime.datetime.now()
        i = 0
        while i <4:
            four_months_name.append((today - datetime.timedelta(days = 30 * i)).strftime("%b"))
            four_months_number.append((today - datetime.timedelta(days = 30 * i)).strftime('%m'))
            four_months_year.append((today - datetime.timedelta(days = 30 * i)).strftime('%Y'))
            i += 1
        
        '''
        Find sales data for previous four months
        1. Find user devices
        2. find sales data for each devices
        '''
        devices = device_info.objects.filter(user_id_id = request.session['user_id'])

        temp_data = []
        d = {}
        for i in range(len(devices)):
            for j in range(len(four_months_name)):
                d[four_months_name[j]] = sales_track.objects.filter(device_id_id = devices[i].id, date_created__range =(datetime.date(int(four_months_year[j]),int(four_months_number[j]),1)  , datetime.date(int(four_months_year[j]),int(four_months_number[j]),calendar.monthrange(int(four_months_year[j]),int(four_months_number[j]))[-1]))).aggregate(Sum('sales'))['sales__sum']
                #temp_data[i][four_months_name[j]] = sales_track.objects.filter(device_id_id = devices[i].id, date_created__range =(datetime.date(int(four_months_year[j]),int(four_months_number[j]),1)  , datetime.date(int(four_months_year[j]),int(four_months_number[j]),calendar.monthrange(int(four_months_year[j]),int(four_months_number[j]))[-1]))).aggregate(Sum('sales'))['sales__sum']
                if d[four_months_name[j]] == None:
                    d[four_months_name[j]] = 0
            temp_data.append(dict(d))

        month_label = four_months_name
        device_label = [p.device_label for p in devices]
        monthly_data = temp_data
        data = [month_label,device_label,monthly_data]
        data = json.dumps(data)
        try:
            return HttpResponse(data,content_type = 'application/json')
        except Exception as e:
            return(e)
    else:
        return HttpResponse("")


def ajax_return_pie_data(request):
    if request.is_ajax():
        total_sale = []
        devices = device_info.objects.filter(user_id_id = request.session['user_id'])
        for p in devices:
            total_sale.append(sales_track.objects.filter(device_id_id = p.id).aggregate(Sum('sales')))
        x = [x.device_label for x in devices]
        data = [x,total_sale]
        data = json.dumps(data)
        return HttpResponse(data,content_type = 'application/json')

def ajax_return_data_for_statistics(request):
    if request.is_ajax():
        try:
            four_months_name = []
            four_months_number = []
            four_months_year = []
            today = datetime.datetime.now()
            i = 0
            month = 12
            while i <month:
                four_months_name.append((today - datetime.timedelta(days = 31 * i)).strftime("%b"))
                four_months_number.append((today - datetime.timedelta(days = 31 * i)).strftime('%m'))
                four_months_year.append((today - datetime.timedelta(days = 31 * i)).strftime('%Y'))
                i += 1

            devices = device_info.objects.filter(user_id_id = request.session['user_id'])
            data_holder = []
            d = {}
            print(four_months_name)
            for i in range(len(devices)):
                j = 0
                while j < len(four_months_name):
                    x = sales_track.objects.filter(device_id_id = devices[i].id, date_created__range = (datetime.date(int(four_months_year[j]),int(four_months_number[j]),1)  , datetime.date(int(four_months_year[j]),int(four_months_number[j]),calendar.monthrange(int(four_months_year[j]),int(four_months_number[j]))[-1]))).aggregate(Sum('sales'))['sales__sum']
                    if x == None:
                        x = 0
                    d[four_months_name[j]] = x
                    j += 1
                data_holder.append(dict(d))
            # Here comes ML part
            next_months_name = []
            next_months_number = []
            next_months_year = []
            next_months = 13
            i = 1
            while i < next_months:
                next_months_name.append((today + datetime.timedelta(days = 31 * i)).strftime("%b"))
                next_months_number.append((today + datetime.timedelta(days = 31 * i)).strftime('%m'))
                next_months_year.append((today + datetime.timedelta(days = 31 * i)).strftime('%Y'))
                i += 1
            d = {} # dict Holder
            device_prediction_holder = []
            for i in range(len(devices)):
                dataset = []
                for j in range(len(four_months_name)):
                    dataset.append([four_months_number[j],four_months_year[j]])

                x = np.asarray(dataset)
                y = list(data_holder[i].values())
                lr = LinearRegression()
                # print(data_holder[0])
                lr.fit(x,y)
                
                # Predictions for next months
                i = 1
                while i < (len(next_months_name)):
                    d[next_months_name[i]] = lr.predict([[float(next_months_number[i]),float(next_months_year[i])]])[0]
                    i += 1
                device_prediction_holder.append(d)
                d = {}
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Dec']
            real_data = []
            predicted_data = []
            for i in range(len(devices)):
                real_data.append(dict(OrderedDict(sorted(data_holder[i].items(),key =lambda x:months.index(x[0])))))
                predicted_data.append(dict(OrderedDict(sorted(device_prediction_holder[i].items(),key =lambda x:months.index(x[0])))))

            data = [months[:-1],[p.id for p in devices],real_data,predicted_data]
            data = json.dumps(data)
            return HttpResponse(data,content_type = 'application/json')
        except Exception as e:
            return HttpResponse(e)

def ajax_return_live_data(request):
    today = datetime.datetime.now()
    data = []
    if request.is_ajax():
        try:
            deivces = device_info.objects.filter(user_id_id = request.session['user_id'])
            data = sales_track.objects.filter(device_id_id__in = [p.id for p in deivces]).order_by('-date_created')[:10]
            # data = json.dumps(data)
            # return JsonResponse(data)
            temp_label_holder = []
            for each_device_id in data:
                temp_label_holder.append(device_info.objects.get(id = each_device_id.device_id_id).device_label)
        
            data_id = [p.id for p in data]
            data_label = temp_label_holder
            data_date = [p.date_created.strftime('%d/%m/%y, %H:%M') for p in data]
            data_data = [p.sales for p in data]

            data = json.dumps([data_id,data_label,data_data,data_date])
            return HttpResponse(data,content_type = 'application/json')
        except Exception as e:
            return HttpResponse(e)
