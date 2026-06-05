from app import create_app

app = create_app()

@app.cli.command('show-bookings')
def show_bookings():
    """Prints all bookings in the database in a clean ASCII table."""
    from app.models.booking import Booking
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    print(f"\n================= LIVE TICKET BOOKINGS ({len(bookings)} Total) =================")
    print(f"{'ID':<5} | {'PNR':<12} | {'User':<15} | {'Seats':<10} | {'Price (Rs)':<10} | {'Status':<10} | {'Journey Date':<12}")
    print("-" * 90)
    for b in bookings:
        seats = ", ".join([str(p.seat_number) for p in b.passengers])
        user_name = b.user.username if b.user else f"ID: {b.user_id}"
        journey_date = b.schedule.journey_date.strftime('%Y-%m-%d') if b.schedule else 'N/A'
        print(f"{b.id:<5} | {b.pnr:<12} | {user_name:<15} | {seats:<10} | {b.total_amount:<10.2f} | {b.status:<10} | {journey_date:<12}")
    print("========================================================================\n")

if __name__ == '__main__':
    # Run the application locally in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
