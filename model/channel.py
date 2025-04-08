# channel.py
from sqlite3 import IntegrityError
from sqlalchemy import Text, JSON
from __init__ import app, db
from model.group import Group

class Channel(db.Model):
    """
    Channel Model
    
    The Channel class represents a channel within a group, with customizable attributes.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the channel.
        _name (db.Column): A string representing the name of the channel.
        _attributes (db.Column): A JSON blob representing customizable attributes for the channel.
        _group_id (db.Column): An integer representing the group to which the channel belongs.
    """
    __tablename__ = 'channels'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), nullable=False)
    _attributes = db.Column(JSON, nullable=True)
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

    posts = db.relationship('Post', backref='channel', lazy=True)

    def __init__(self, name, group_id, attributes=None):
        """
        Constructor, 1st step in object creation.
        
        Args:
            name (str): The name of the channel.
            group_id (int): The group to which the channel belongs.
            attributes (dict, optional): Customizable attributes for the channel. Defaults to None.
        """
        self._name = name
        self._group_id = group_id
        self._attributes = attributes or {}

    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr() built-in function.
        
        Returns:
            str: A text representation of how to create the object.
        """
        return f"Channel(id={self.id}, name={self._name}, group_id={self._group_id}, attributes={self._attributes})"
    
    @property
    def name(self):
        """
        Gets the channel's name.
        
        Returns:
            str: The channel's name.
        """
        return self._name

    def create(self):
        """
        The create method adds the object to the database and commits the transaction.
        
        Uses:
            The db ORM methods to add and commit the transaction.
        
        Raises:
            Exception: An error occurred when adding the object to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        
        Returns:
            dict: A dictionary containing the channel data.
        """
        return {
            'id': self.id,
            'name': self._name,
            'attributes': self._attributes,
            'group_id': self._group_id
        }
        
    def update(self, inputs):
        """
        Updates the channel object with new data.
        
        Args:
            inputs (dict): A dictionary containing the new data for the channel.
        
        Returns:
            Channel: The updated channel object, or None on error.
        """
        if not isinstance(inputs, dict):
            return self

        name = inputs.get("name", "")
        group_id = inputs.get("group_id", None)

        # Update table with new data
        if name:
            self._name = name
        if group_id:
            self._group_id = group_id

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self
        
    @staticmethod
    def restore(data):
        channels = {}
        for channel_data in data:
            _ = channel_data.pop('id', None)  # Remove 'id' from channel_data
            name = channel_data.get("name", None)
            channel = Channel.query.filter_by(_name=name).first()
            if channel:
                channel.update(channel_data)
            else:
                channel = Channel(**channel_data)
                channel.create()
        return channels
    
def initChannels():
    """
    The initChannels function creates the Channel table and adds tester data to the table.
    
    Uses:
        The db ORM methods to create the table.
    
    Instantiates:
        Channel objects with tester data.
    
    Returns:
        list: A list of created Channel objects.
    
    Raises:
        IntegrityError: An error occurred when adding the tester data to the table.
    """
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""

        # Get all groups
        general = Group.query.filter_by(_name='General').first()
        support = Group.query.filter_by(_name='Support').first()
        chess_champion = Group.query.filter_by(_name='Chess Champion').first()
        underground_music = Group.query.filter_by(_name='Underground Music').first()
        internet_debates = Group.query.filter_by(_name='Internet Debates').first()
        calico_vote = Group.query.filter_by(_name='Calico Vote').first()
        dnero_store = Group.query.filter_by(_name='Dnero Store').first()
        nfl_goats = Group.query.filter_by(_name='NFL GOATs').first()
        car_debates = Group.query.filter_by(_name='Car Debates').first()
        
        # Create channels for each group
        channels = []
        created_channels = []
        
        # Home Page Channels
        if general:
            channels.extend([
                Channel(name='Announcements', group_id=general.id),
                Channel(name='Events', group_id=general.id)
            ])
        
        if support:
            channels.extend([
                Channel(name='FAQ', group_id=support.id),
                Channel(name='Help Desk', group_id=support.id)
            ])
        
        # Chess Champion Channels
        if chess_champion:
            channels.extend([
                Channel(name='General', group_id=chess_champion.id),
                Channel(name='Chess Tips', group_id=chess_champion.id),
                Channel(name='Game Updates', group_id=chess_champion.id)
            ])
        
        # Underground Music Channels
        if underground_music:
            channels.extend([
                Channel(name='Artists', group_id=underground_music.id),
                Channel(name='Songs', group_id=underground_music.id),
                Channel(name='Genres', group_id=underground_music.id)
            ])
        
        # Internet Debates Channels
        if internet_debates:
            channels.extend([
                Channel(name='Milk vs Cereal', group_id=internet_debates.id),
                Channel(name='Hot Dog Sandwich', group_id=internet_debates.id),
                Channel(name='Pineapple on Pizza', group_id=internet_debates.id),
                Channel(name='Cats vs Dogs', group_id=internet_debates.id),
                Channel(name='Coffee or Tea', group_id=internet_debates.id)
            ])
        
        # Calico Vote Channels
        if calico_vote:
            channels.extend([
                Channel(name='Adventure Play House', group_id=calico_vote.id),
                Channel(name='Sylvanian Family Restraunt House', group_id=calico_vote.id),
                Channel(name='Magical Mermaid Castle House', group_id=calico_vote.id),
                Channel(name='Woody School House', group_id=calico_vote.id),
                Channel(name='Spooky Suprise Haunted House', group_id=calico_vote.id),
                Channel(name='Brick Oven Bakery House', group_id=calico_vote.id)
            ])
        
        # Dnero Store Channels
        if dnero_store:
            channels.extend([
                Channel(name='Food and Drink', group_id=dnero_store.id),
                Channel(name='Spirit', group_id=dnero_store.id),
                Channel(name='Limited Edition', group_id=dnero_store.id),
                Channel(name='Gift Cards', group_id=dnero_store.id)
            ])
        
        # NFL GOATs Channels
        if nfl_goats:
            channels.extend([
                Channel(name='Quarterbacks', group_id=nfl_goats.id),
                Channel(name='Running Backs', group_id=nfl_goats.id),
                Channel(name='Wide Receivers', group_id=nfl_goats.id),
                Channel(name='Defensive Players', group_id=nfl_goats.id),
                Channel(name='NFL Divisions', group_id=nfl_goats.id)
            ])
        
        # Car Debates Channels
        if car_debates:
            channels.extend([
                Channel(name='Economy Cars', group_id=car_debates.id),
                Channel(name='Luxury Cars', group_id=car_debates.id),
                Channel(name='Vintage Cars', group_id=car_debates.id),
                Channel(name='Student Cars', group_id=car_debates.id)
            ])
        
        # Add all channels to the session
        for channel in channels:
            try:
                db.session.add(channel)
                db.session.flush()  # Flush to get the channel IDs
                created_channels.append(channel)
                print(f"Record created: {repr(channel)}")
            except IntegrityError:
                db.session.rollback()
                print(f"Channel already exists: {channel.name}")
                # Try to get the existing channel
                existing = Channel.query.filter_by(_name=channel._name, _group_id=channel._group_id).first()
                if existing:
                    created_channels.append(existing)
                continue
        
        # Commit all changes at once
        try:
            db.session.commit()
            print("All channels created successfully")
            return created_channels
        except Exception as e:
            db.session.rollback()
            print(f"Error committing channels: {str(e)}")
            return None
