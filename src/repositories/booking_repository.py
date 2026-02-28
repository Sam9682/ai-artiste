"""Repository for booking persistence."""

from typing import Optional, List
from sqlalchemy.orm import Session
import json
from datetime import datetime

from src.models import Booking, Result, ErrorDetails, ErrorCode
from src.models.date_range import DateRange
from src.models.enums import BookingStatus
from .models import BookingDB


class BookingRepository:
    """Repository for managing booking persistence."""
    
    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create(self, booking: Booking) -> Result[Booking]:
        """
        Create a new booking in the database.
        
        Args:
            booking: The booking to create
            
        Returns:
            Result containing the created booking or error details
        """
        try:
            db_booking = BookingDB(
                id=booking.id,
                artist_id=booking.artist_id,
                venue_id=booking.venue_id,
                status=booking.status,
                period_json=self._serialize_period(booking.period),
                created_at=booking.created_at,
                confirmed_at=booking.confirmed_at
            )
            
            self.session.add(db_booking)
            self.session.commit()
            self.session.refresh(db_booking)
            
            return Result.ok(self._to_domain_model(db_booking))
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to create booking: {str(e)}"
            ))
    
    def get_by_id(self, booking_id: str) -> Result[Booking]:
        """
        Retrieve a booking by ID.
        
        Args:
            booking_id: The ID of the booking to retrieve
            
        Returns:
            Result containing the booking or error details
        """
        try:
            db_booking = self.session.query(BookingDB).filter(
                BookingDB.id == booking_id
            ).first()
            
            if db_booking is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Booking with ID '{booking_id}' not found"
                ))
            
            return Result.ok(self._to_domain_model(db_booking))
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve booking: {str(e)}"
            ))
    
    def get_by_artist_id(self, artist_id: str) -> Result[List[Booking]]:
        """
        Retrieve all bookings for an artist.
        
        Args:
            artist_id: The ID of the artist
            
        Returns:
            Result containing list of bookings or error details
        """
        try:
            db_bookings = self.session.query(BookingDB).filter(
                BookingDB.artist_id == artist_id
            ).all()
            
            bookings = [self._to_domain_model(db_booking) for db_booking in db_bookings]
            return Result.ok(bookings)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve bookings for artist: {str(e)}"
            ))
    
    def get_by_venue_id(self, venue_id: str) -> Result[List[Booking]]:
        """
        Retrieve all bookings for a venue.
        
        Args:
            venue_id: The ID of the venue
            
        Returns:
            Result containing list of bookings or error details
        """
        try:
            db_bookings = self.session.query(BookingDB).filter(
                BookingDB.venue_id == venue_id
            ).all()
            
            bookings = [self._to_domain_model(db_booking) for db_booking in db_bookings]
            return Result.ok(bookings)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve bookings for venue: {str(e)}"
            ))
    
    def get_confirmed_bookings(self) -> Result[List[Booking]]:
        """
        Retrieve all confirmed bookings.
        
        Returns:
            Result containing list of confirmed bookings or error details
        """
        try:
            db_bookings = self.session.query(BookingDB).filter(
                BookingDB.status == BookingStatus.CONFIRMED
            ).all()
            
            bookings = [self._to_domain_model(db_booking) for db_booking in db_bookings]
            return Result.ok(bookings)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve confirmed bookings: {str(e)}"
            ))
    
    def update(self, booking: Booking) -> Result[Booking]:
        """
        Update an existing booking.
        
        Args:
            booking: The booking with updated data
            
        Returns:
            Result containing the updated booking or error details
        """
        try:
            db_booking = self.session.query(BookingDB).filter(
                BookingDB.id == booking.id
            ).first()
            
            if db_booking is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Booking with ID '{booking.id}' not found"
                ))
            
            # Update fields
            db_booking.artist_id = booking.artist_id
            db_booking.venue_id = booking.venue_id
            db_booking.status = booking.status
            db_booking.period_json = self._serialize_period(booking.period)
            db_booking.confirmed_at = booking.confirmed_at
            
            self.session.commit()
            self.session.refresh(db_booking)
            
            return Result.ok(self._to_domain_model(db_booking))
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to update booking: {str(e)}"
            ))
    
    def delete(self, booking_id: str) -> Result[None]:
        """
        Delete a booking.
        
        Args:
            booking_id: The ID of the booking to delete
            
        Returns:
            Result indicating success or error details
        """
        try:
            db_booking = self.session.query(BookingDB).filter(
                BookingDB.id == booking_id
            ).first()
            
            if db_booking is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Booking with ID '{booking_id}' not found"
                ))
            
            self.session.delete(db_booking)
            self.session.commit()
            
            return Result.ok(None)
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to delete booking: {str(e)}"
            ))
    
    def get_all(self) -> Result[List[Booking]]:
        """
        Retrieve all bookings.
        
        Returns:
            Result containing list of bookings or error details
        """
        try:
            db_bookings = self.session.query(BookingDB).all()
            bookings = [self._to_domain_model(db_booking) for db_booking in db_bookings]
            return Result.ok(bookings)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve bookings: {str(e)}"
            ))
    
    def _serialize_period(self, period: DateRange) -> str:
        """Serialize period to JSON."""
        return json.dumps({
            'id': period.id,
            'start_date': period.start_date.isoformat(),
            'end_date': period.end_date.isoformat()
        })
    
    def _deserialize_period(self, json_str: str) -> DateRange:
        """Deserialize period from JSON."""
        data = json.loads(json_str)
        return DateRange(
            id=data['id'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date'])
        )
    
    def _to_domain_model(self, db_booking: BookingDB) -> Booking:
        """Convert database model to domain model."""
        return Booking(
            id=db_booking.id,
            artist_id=db_booking.artist_id,
            venue_id=db_booking.venue_id,
            period=self._deserialize_period(db_booking.period_json),
            status=db_booking.status,
            created_at=db_booking.created_at,
            confirmed_at=db_booking.confirmed_at
        )
