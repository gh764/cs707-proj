package edu.wisc.cs707.io;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.src.PointsOfInterest;
import edu.wisc.cs707.util.LocationController;

public class DatabaseHandler extends SQLiteOpenHelper {

	private static final int DATABASE_VERSION = 1;
	private static final String DATABASE_NAME = "MobilityManagerDatabase";
		
	DatabaseHandler(Context context) {
		super(context, DATABASE_NAME, null, DATABASE_VERSION);
	}	
	
	@Override
	public void onCreate(SQLiteDatabase db) {		
		/* create tables. */
		db.execSQL("create table if not exists [poi] (" + "\n" +
						"[pid]			[integer]	primary key," + "\n" +
						"[name]			[text] 		not null," + "\n" +
						"[description] 	[text],				 " + "\n" + 
						"[longitude] 	[real] 		not null," + "\n" +
						"[latitude] 	[real] 		not null," + "\n" +
						"[altitude] 	[int],				 " + "\n" +
						"[radius] 		[int]		not null 	check(radius > 0)," + "\n" +
						"[monitored] 	[int] 		not null 	check(monitored in (0,1))	default 0" + "\n" + 
		    	")");
		
		db.execSQL("create table if not exists [model] (" + "\n" +
	    				"[mid]							[integer]			primary key," + "\n" +

	    				"[schedule]						[char]  not null    default 'r' check([schedule] in ('r', 'i'))," + "\n" +
	    				"[type]							[char]  not null    default 's' check([type] in ('c', 's'))," + "\n" +
	    				
	    				"[version]						[int]   not null    default 0," + "\n" +
	    				"[created_on]					[date]  not null    default current_date," + "\n" +
	    				"[last_updated_on]				[date]  not null    default current_date," + "\n" +
	    				"[earliest_rebuild]				[int]   not null    default 7," + "\n" +
	    				"[expires_in]					[int]   not null    default 90," + "\n" +

	    				"[update_freq]					[real]	not null	default 5," + "\n" +				
	    				"[window_size]					[int]   not null    default 2   check([window_size] >= 2 and [window_size] <= 24)," + "\n" +
	    				"[agg_fx]						[char]  not null    default 'a' check([agg_fx] in ('a', 'w'))," + "\n" +
	    				"[granularity]					[int]   not null    default 15  check([granularity] > 0 & [granularity] < 120)," + "\n" +
	    				
	    				"[nr_matches]					[int]   not null    default 0," + "\n" +
	    				"[nr_successful]				[int]   not null    default 0," + "\n" +
	    				"[streak]						[int]   not null    default 0," + "\n" +
	    				"[last10]						[int]   not null    default 0," + "\n" +

	    				"[rebuild]						[int]   not null    default 0   check([rebuild] = 0 or [rebuild] = 1)," + "\n" +
	    				"[total_mismatch_trig]			[real]  not null    default 0.5 check([total_mismatch_trig] >= 0 and [total_mismatch_trig] <= 1)," + "\n" +
	    				"[mismatch_strk_trig]			[int]   not null    default 5   check([mismatch_strk_trig] >= 0)," + "\n" +
	    				"[last10_mismatch_strk_trig]	[real]  not null    default 0.5 check([last10_mismatch_strk_trig] >= 0 and [last10_mismatch_strk_trig] <= 1)" + "\n" +
	    	    ")");
		
		db.execSQL("create table if not exists [location_snapshot] (" + "\n" +
	    				"[location] 	[int]		not null	references [poi](pid)," + "\n" +
	    				"[entered]  	[datetime]	not null," + "\n" +
	    				"[exited]		[datetime]  not null" + "\n" +
	    	    ")");

			/*
	    	# create subscriber table. 
	    	c.execute('''
	    	    create table if not exists [subscriber] (
	    		[sid]	        [integer]           primary key,
	    		[uid]	        [int]   not null    references [usr]([uid]),
	    	        [name]          [text]  not null,
	    	        [enbl_alrts]    [int]   not null    default 0
	    	    )
	    	''')

	    	# agg_location_snapshot table.
	    	c.execute('''
	    	    create table if not exists [agg_location_snapshot] (
	    	        [mid]           [int]   not null,    
	    	        [version]       [int]   not null,

	    	        [day]           [int]   not null    check([day] in (0,1,2,3,4,5,6)),
	    	        [start]         [int]   not null,
	    	        [end]           [int]   not null,
	    	        [cxl_thrshld]   [int]               default 15,
	    	        [location]      [int]               references [poi](pid),
	    	        
	    	        foreign key([mid], [version]) references [model]([mid], [version])
	    	    )
	    	''')

	    	# alert table.
	    	c.execute('''
	    	    create table if not exists [alert] (
	    	        [aid]           [integer]                       primary key,
	    	        [sid]           [int]   not null                references [subscriber]([sid]),

	    	        [event]         [char]  not null                check([event] in ('a', 'd')),
	    	        [location]      [int]   not null                references [poi]([pid]),
	    	        [send_within]   [int],

	    	        [is_enabled]    [int]   not null    default 0
	    	    )
	    	''')
	    	*/
	}

	@Override
	public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
		
	}

	PointsOfInterest loadPointsOfInterest() {
		PointsOfInterest locations = new PointsOfInterest();
		
		SQLiteDatabase db = super.getReadableDatabase();
		
		String [] columns = new String[]{"pid", "name", "latitude", "longitude",
				"monitored", "altitude", "radius"};
	
		
		Cursor c = db.query("poi", columns, null, null, null, null, null);
		
		while (c.moveToNext()) {
			int id = c.getInt(c.getColumnIndex("pid"));
			String name = c.getString(c.getColumnIndex("name"));
			double latitude = c.getDouble(c.getColumnIndex("latitude"));
			double longitude = c.getDouble(c.getColumnIndex("longitude"));
			int altitude = c.getInt(c.getColumnIndex("altitude"));
			int radius = c.getInt(c.getColumnIndex("radius"));
			boolean monitored = c.getInt(c.getColumnIndex("monitored")) != 0;
			
			locations.add(new PointOfInterest(id, name, latitude, longitude, radius, altitude, monitored));
		} 
		db.close();
		
		return locations;
	}

	void save(PointOfInterest poi) {
		
		ContentValues values = new ContentValues();
		values.put("name", poi.getName());
		values.put("latitude", poi.getLatitude());
		values.put("longitude", poi.getLongitude());
		values.put("altitude", poi.getAltitude());
		values.put("radius", poi.getRadius());
		values.put("monitored", poi.isMonitored() ? 1 : 0);
		
		SQLiteDatabase db = super.getWritableDatabase();
	
		if (poi.getId() < 0) {
			poi.setId((int)db.insert("poi", "pid", values));
		} else {
			db.update("poi", values, "pid=?", new String[]{String.valueOf(poi.getId())});
		}
		
		db.close();
	}
	
	void save(LocationController.Snapshot snapshot) {
		ContentValues values = new ContentValues();
		
		values.put("location", snapshot.getPoi().getId());
		values.put("entered", snapshot.getTimeEntered());
		values.put("exited", snapshot.getTimeExited());
		
		SQLiteDatabase db = getWritableDatabase();
		db.insert("location_snapshot", null, values);
		
		db.close(); 
	}
}
