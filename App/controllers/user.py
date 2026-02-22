from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from App import db 
from App.models import User, Parking_Lot, Parking_Spot, Reserving_Spot, Admin
from App.decorators import roles_required
user = Blueprint("user", __name__)

@user.route("/user_dashboard")
@login_required
@roles_required("user")
def user_dashboard():
    ParkingLot=Parking_Lot.query.filter_by(is_active=True).all()
    ParkingSpot={lot.id: Parking_Spot.query.filter_by(is_active=True,lot_id=lot.id, status="A").all() for lot in ParkingLot }
    now=datetime.utcnow()+ timedelta(hours=5, minutes=30)
    active_booking= Reserving_Spot.query.filter_by(user_id=current_user.id, leaving_time=None).first()
    return render_template('userhome.html', User=current_user, ParkingLot=ParkingLot, ParkingSpot=ParkingSpot, now=now, active_booking=active_booking)

@user.route("/search")
@login_required
@roles_required("user")
def search():
    query=request.args.get('q','')
    ParkingLot = Parking_Lot.query.filter(Parking_Lot.is_active == True,
    (Parking_Lot.address.ilike(f'%{query}%')) |
    (Parking_Lot.pincode.like(f'%{query}%')) |
    (Parking_Lot.prime_location_name.ilike(f'%{query}%'))).all()
    ParkingSpot={lot.id: Parking_Spot.query.filter_by(is_active=True, lot_id=lot.id, status="A").all() for lot in ParkingLot }
    now=datetime.utcnow()+ timedelta(hours=5, minutes=30)
    return render_template('userhome.html', User=current_user, ParkingLot=ParkingLot, ParkingSpot=ParkingSpot, query=query, now=now)

@user.route("/book_spot", methods=["POST"])
@login_required
@roles_required("user")
def book_spot():
    user_id=request.form['user_id']
    spot_id=request.form['spot_id']
    vehicle_no =request.form['vehicle_no']
    parking_time=datetime.utcnow()+ timedelta(hours=5, minutes=30)
    new_reserving_spot=Reserving_Spot(spot_id=spot_id, user_id=user_id, parking_time=parking_time, vehicle_no=vehicle_no)
    ParkingSpot=Parking_Spot.query.get_or_404(spot_id)
    ParkingSpot.status="O"
    db.session.add(new_reserving_spot)
    db.session.commit()
    return redirect(url_for("user.user_dashboard"))

@user.route("/release_spot/<int:id>")
@login_required
@roles_required("user")
def release_spot(id):
    reserved=Reserving_Spot.query.get_or_404(id)
    start=reserved.parking_time
    now=datetime.utcnow()+ timedelta(hours=5, minutes=30)
    time=now-start
    price=float(reserved.spot.lot.price)
    cost=round(price*time.total_seconds()/3600, 2)
    hours= time.total_seconds()//3600 
    minutes= (time.total_seconds()%3600)//60 
    duration=f"{hours} hr {minutes} min"
    reserved.cost=cost
    db.session.commit()
    return render_template("userhome.html", duration=duration, now=now, User=current_user, active_booking=reserved, cost=cost)

@user.route("/released_spot/<int:id>/<string:now>")
@login_required
@roles_required("user")
def released_spot(id, now):
    reservation= Reserving_Spot.query.get_or_404(id)
    spot=reservation.spot_id
    reservation.leaving_time=datetime.strptime(now, "%Y-%m-%d %H:%M:%S.%f")
    reservedspot= Parking_Spot.query.get(spot)
    reservedspot.status="A"
    db.session.commit()
    return redirect(url_for("user.summary"))

@user.route("/summary")
@login_required
@roles_required("user")
def summary():
    user=current_user
    lot_costs={}
    for res in Reserving_Spot.query.filter_by(user_id=current_user.id).order_by(Reserving_Spot.parking_time.asc()):
        cost=0
        if res.leaving_time is not None :
            cost+=res.cost
        if res.spot.lot.prime_location_name not in lot_costs.keys():
            lot_costs[res.spot.lot.prime_location_name]=0
        lot_costs[res.spot.lot.prime_location_name]+=cost
    reservations = Reserving_Spot.query.filter_by(user_id=current_user.id).order_by(Reserving_Spot.parking_time.desc()).all()
    return render_template('usersummary.html', cost=list(lot_costs.values()), labels=list(lot_costs.keys()), User=user, reservations=reservations)

@user.route("/usereditprofile", methods=["POST"])
@login_required
@roles_required("user")
def usereditprofile():
    user=User.query.get(current_user.id)
    user.name=request.form['name']
    user.username=request.form['username']
    user.address= request.form['address']
    user.pincode= request.form['pincode']
    password=request.form['password']
    if password:
        password= generate_password_hash(password)
        user.password= password
    db.session.commit()
    return redirect(url_for("user.user_dashboard"))



