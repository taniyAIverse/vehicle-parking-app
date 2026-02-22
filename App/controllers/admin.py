from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from  werkzeug.security import generate_password_hash

from App import db 
from App.models import User, Parking_Lot, Parking_Spot, Reserving_Spot, Admin
from App.decorators import roles_required  

admin = Blueprint("admin", __name__)

@admin.route("/admin_dashboard")
@login_required
@roles_required("admin")
def admin_dashboard():
    ParkingLot=Parking_Lot.query.filter_by(is_active=True).all()
    return render_template('adminhome.html', ParkingLot=ParkingLot, admin=current_user)

@admin.route("/addlot", methods=['POST'])
@login_required
@roles_required("admin")
def add_lot():
    if request.method == "POST":
        prime_location_name = request.form["prime_location_name"]
        address = request.form["address"]
        pincode= request.form["pincode"]
        price= float(request.form["price"])
        max_spots = int(request.form["max_spots"])
        
        new_parkinglot = Parking_Lot(prime_location_name=prime_location_name, address=address, pincode=pincode, price=price, max_spots=max_spots)
        db.session.add(new_parkinglot)
        db.session.flush()
        for  i in range(max_spots):
            new_spot=Parking_Spot(lot_id=new_parkinglot.id)
            db.session.add(new_spot)
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))

@admin.route("/editlot/<int:id>", methods=["POST"])
@login_required
@roles_required("admin")
def edit_lot(id):
    if request.method == "POST":
        parkinglot=Parking_Lot.query.get_or_404(id)
        parkinglot.prime_location_name = request.form["prime_location_name"]
        parkinglot.address= request.form["address"]
        parkinglot.pincode= request.form['pincode']
        parkinglot.price= float(request.form['price'])
        old_spots=parkinglot.max_spots
        new_spots=int(request.form['max_spots'])
        active_spots=[spot for spot in parkinglot.spots if spot.is_active] 
        active_count=len(active_spots)
        if active_count<new_spots:
            for i in range(new_spots-active_count):
                spot=Parking_Spot(lot_id=id)
                db.session.add(spot)
        elif active_count>new_spots:
            available=[spot for spot in active_spots if spot.status=="A" ]
            if len(available)>= (active_count - new_spots):
                for spot in available[:active_count- new_spots]:
                    spot.is_active = False
        else:
            flash("Some spots are still active. Reduce only available spots.", "danger")
            return redirect(url_for('admin.admin_dashboard'))

        
        parkinglot.max_spots=new_spots
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))

@admin.route("/Deletelot/<int:id>", methods=["POST"])
@login_required
@roles_required("admin")
def delete_lot(id):
    parkinglot=Parking_Lot.query.get_or_404(id)
    parkingspot=[spot for spot in parkinglot.spots if spot.is_active]
    for spot in parkingspot:
        if spot.status=="O":
            flash("Can't delete lot with occupied spots.", "warning")
            return redirect(url_for("admin.admin_dashboard"))
    parkinglot.is_active=False
    for spot in parkinglot.spots:
        spot.is_active=False
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@admin.route("/ViewSpot/<int:id>", methods=["GET","POST"])
@login_required
@roles_required("admin")
def view_spot(id):
    Parkinglot=Parking_Lot.query.get_or_404(id)
    ParkingSpots=[ spot for spot in Parkinglot.spots if spot.is_active]
    reserved={spot.id: Reserving_Spot.query.filter_by(spot_id=spot.id).order_by(Reserving_Spot.parking_time.desc()).first() for spot in ParkingSpots}
    now=datetime.utcnow()+ timedelta(hours=5, minutes=30)
    return render_template("adminparkingspot.html", ParkingSpot=ParkingSpots, Parkinglot=Parkinglot, reserved=reserved, now=now, admin=current_user)

@admin.route("/Adminsummary")
@login_required
@roles_required("admin")
def summary():
    Revenue={}
    for lot in Parking_Lot.query.all():
        total_cost=0
        for spot in lot.spots :
            for rspot in Reserving_Spot.query.filter_by(spot_id=spot.id).all():
                if rspot.cost:
                    total_cost+=rspot.cost
        if lot.prime_location_name not in Revenue.keys():
            Revenue[lot.prime_location_name]=0
        Revenue[lot.prime_location_name]+= total_cost
    Reserved={}
    for lot in Parking_Lot.query.filter_by(is_active=True).all():
        A,O=0,0
        active_spot=[spot for spot in lot.spots if spot.is_active ]
        for spot in active_spot:  
            if spot.status=="O":
                O+=1
            else:
                A+=1
        Reserved[lot.id]=(O,A)
    lotids=list(Reserved.keys())
    spotdetail=list(Reserved.values())

    location=list(Revenue.keys())
    revenue=list(Revenue.values())

    return render_template("adminsummary.html", locations=location, revenues=revenue, lotids=lotids, spotdetail=spotdetail, admin=current_user)
   
@admin.route("/userdetail")
@login_required
@roles_required("admin")
def usersdetail():
    return render_template("adminusers.html", Users=User.query.all(), admin=current_user)


@admin.route("/editprofile", methods=["POST"])
@login_required
@roles_required("admin")
def editprofile():
    admin=Admin.query.get(current_user.id)
    admin.name=request.form['name']
    admin.username=request.form['username']
    password=request.form['password']
    if password:
        password= generate_password_hash(password)
        admin.password= password
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

