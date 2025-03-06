import os
import datetime
from orator import DatabaseManager, Model,  Schema

# Load environment variables
MYSQL_USER = os.getenv("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Temp@1234")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_DB = os.getenv("MYSQL_DB", "call_data")

# MySQL Database Configuration for Orator
DATABASES = {
    'mysql': {
        'driver': 'mysql',
        'host': MYSQL_HOST,
        'database': MYSQL_DB,
        'user': MYSQL_USER,
        'password': MYSQL_PASSWORD,
        'prefix': '',
        'port': MYSQL_PORT
    }
}

# Initialize Database Manager
db = DatabaseManager(DATABASES)
Model.set_connection_resolver(db)
schema = Schema(db)

### **📞 Call Data Model**
class CallRecord(Model):
    __table__ = "call_records"
    __primary_key__ = "id"
    
    __fillable__ = [
        "call_sid", "phone_number", "name", "first_name", "last_name", 
        "email", "call_status", "start_time", "end_time", "duration_seconds", 
        "call_type", "email_sent",
    ]
    __timestamps__ = False  # Disabling auto timestamps

### **✅ Function to Update Call Record**
def update_call(call_sid, name=None, email=None):
    call = CallRecord.where("call_sid", call_sid).first()
    if call:
        call.name = name or call.name
        call.email = email or call.email
        call.call_status = "completed"
        call.end_time = datetime.datetime.utcnow()
        if call.start_time:
            call.duration_seconds = (call.end_time - call.start_time).seconds
        call.save()
        return True
    return False

### **📞 Function to Retrieve Call Details**
def get_call(call_sid):
    return CallRecord.where("call_sid", call_sid).first()

### **🛠 Initialize Database**
def init_db():   
    if not schema.has_table("call_records"):
        with schema.create('call_records') as table:
            table.increments("id"),
            table.string("call_sid", 255).unique().not_null(),
            table.string("phone_number", 20).not_null(),
            table.string("name", 255).nullable(),
            table.string("first_name", 255).nullable(),
            table.string("last_name", 255).nullable(),
            table.string("email", 255).nullable(),
            table.string("call_status", 20).default("ongoing"),
            table.datetime("start_time").nullable(),
            table.datetime("end_time").nullable(),
            table.integer("duration_seconds").nullable(),
            table.string("call_type", 20).default("outbound"),
            table.timestamps()
        print("📂 MySQL Table 'call_records' Created!")

## **🏃‍♂️ Run This to Initialize DB**
if __name__ == "__main__":
    init_db()
