import os
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.get_database('nexus_events')
events_col = db['events']

# Clean existing seed if needed or just add more
seed_events = [
    {
        "id": str(uuid.uuid4()),
        "title": "Global Tech Summit 2026",
        "organizer": "Nexus Tech",
        "date": "2026-04-15",
        "location": "San Francisco, CA",
        "category": "Technology",
        "price": "$299",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "The largest gathering of tech innovators in the world.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Modern Art Exhibition",
        "organizer": "NYC Gallery",
        "date": "2026-05-20",
        "location": "New York, NY",
        "category": "Arts",
        "price": "Free",
        "image": "https://images.unsplash.com/photo-1460661419201-fd4cecea8f82?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Experience the finest modern art from emerging talent.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Sustainable Living Workshop",
        "organizer": "Green Future",
        "date": "2026-03-12",
        "location": "London, UK",
        "category": "Lifestyle",
        "price": "$45",
        "image": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Learn how to live a more sustainable life.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Startup Pitch Night",
        "organizer": "Founders Hub",
        "date": "2026-06-05",
        "location": "Austin, TX",
        "category": "Business",
        "price": "$25",
        "image": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Watch the next unicorn pitch their vision.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Cloud Computing Webinar",
        "organizer": "AWS Experts",
        "date": "2026-02-18",
        "location": "Online",
        "category": "Technology",
        "price": "Free",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Master the cloud with these industry secrets.",
        "type": "Online",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Zen Mindfulness Retreat",
        "organizer": "Peaceful Mind",
        "date": "2026-07-01",
        "location": "Kyoto, Japan",
        "category": "Wellness",
        "price": "$850",
        "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "A week of silence and meditation in nature.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Street Food Carnival",
        "organizer": "Global Eats",
        "date": "2026-08-15",
        "location": "Bangkok, Thailand",
        "category": "Food",
        "price": "$15",
        "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "The world's best street food in one place.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Quantum Physics Colloquium",
        "organizer": "Science Daily",
        "date": "2026-09-22",
        "location": "Berlin, Germany",
        "category": "Education",
        "price": "$120",
        "image": "https://images.unsplash.com/photo-1532094349884-543bb1178329?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Exploring the mysteries of the subatomic world.",
        "type": "In-Person",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "AI Ethics Workshop",
        "organizer": "Futurists Collective",
        "date": "2026-05-10",
        "location": "Online",
        "category": "Technology",
        "price": "$50",
        "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Navigating the murky waters of AI governance.",
        "type": "Online",
        "user_id": "system_seed"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Mountain Biking Challenge",
        "organizer": "Adventure Seekers",
        "date": "2026-10-05",
        "location": "Whistler, Canada",
        "category": "Sports",
        "price": "$75",
        "image": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "description": "Conquer the trails in this epic MTB race.",
        "type": "In-Person",
        "user_id": "system_seed"
    }
]

# Check count before
existing_count = events_col.count_documents({})
print(f"Existing events: {existing_count}")

events_col.insert_many(seed_events)
print(f"Successfully inserted {len(seed_events)} seed events.")

# Check count after
new_count = events_col.count_documents({})
print(f"Total events in DB now: {new_count}")
