package edu.wisc.cs707.util;

import java.util.Vector;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import edu.wisc.cs707.io.StorageHandler;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.src.PointsOfInterest;

public class LocationController implements LocationListener {
	
	public enum Activity {
		Entered,
		Exited;
	};
	
	public class Snapshot {
		
		PointOfInterest poi;
		long entered = 0;
		long exited = 0;
		Activity activity = Activity.Entered;
		
		public PointOfInterest getPoi() {
			return this.poi;
		}
		
		public long getTimeEntered() {
			return this.poi != null ? this.entered : 0;
		}
		
		public boolean exited() {
			return this.poi != null && this.exited != 0 &&
				this.activity == Activity.Exited;
		}
		
		public long getTimeExited() {
			return this.poi != null ? this.exited : 0;
		}
		
		public Activity getActivity() {
			return this.activity;
		}
	}
	
	private static LocationController instance = null;

	private PointsOfInterest pointsOfInterest;
	private Snapshot snapshot = new Snapshot();
	private Location location = null;
	private LocationManager manager = null;
	private String provider = null;
	
	private LocationController(Context c) {		 
		this.pointsOfInterest = StorageHandler.getInstance(c).loadPointsOfInterest();
	}
	
	public static LocationController getInstance(Context context) {
		if (LocationController.instance == null) {
			LocationController.instance = new LocationController(context);
		}
		
		return LocationController.instance;
	}
	
	public PointsOfInterest getPointsOfInterest() {
		return this.pointsOfInterest;
	}
	
	public void set(LocationManager mgr, String provider) {
		this.manager = mgr;
		this.provider = provider;
	}
	
	public Location getlastKnownLocation() {
		if (this.manager != null && this.provider != null) {
			this.onLocationChanged(this.manager.getLastKnownLocation(this.provider));
		}
		return this.location;
	}
	
	public Snapshot getCurrentSnapshot() {
		return this.snapshot;
	}
	
	@Override
	public void onLocationChanged(Location location) {
		
		PointOfInterest p = this.pointsOfInterest.get(
				location.getLatitude(), location.getLongitude(), (int)location.getAccuracy());
		
		if (this.snapshot.poi != null) {
			if (this.snapshot.poi != p &&
					p != null && this.snapshot.poi != PointOfInterest.Unspecified()) {
				this.snapshot.activity = Activity.Exited;
				this.snapshot.exited = location.getTime();
				
				// store snapshot.
				StorageHandler.getInstance(null).save(this.snapshot);
				
				// notify listeners of exit.
				if (this.snapshot.poi != null) {
					this.update_activity_listeners(this.snapshot.activity, this.snapshot);
				}
				// update to new poi
				this.snapshot.poi = p;
				this.snapshot.entered = location.getTime();
				this.snapshot.activity = Activity.Entered;
				
				// notify listeners of new entry.
				if (this.snapshot.poi == null) {
					this.snapshot.poi = PointOfInterest.Unspecified();
				}
				this.update_activity_listeners(this.snapshot.activity, this.snapshot); 
			}
			
		} else {
			this.snapshot.poi = p != null ? p : PointOfInterest.Unspecified();
			this.snapshot.entered = location.getTime();
			this.snapshot.activity = Activity.Entered;
			
			this.update_activity_listeners(this.snapshot.activity, this.snapshot);
		}
		
		this.log(this.location = location);
	}
	
	public Vector<IUserActivityListener> listeners = new Vector<IUserActivityListener>();
	
	public void update_activity_listeners(Activity activity, Snapshot snapshot) {
		for (IUserActivityListener l : this.listeners) {
			l.onUserActivityUpdate(activity, snapshot);
		}
	}
	
	public void requestEntryActivityUpdates(IUserActivityListener l) {
		
	}
	
	public void requestExitActivityUpdates(IUserActivityListener l) {
		
	}
	
	public void requestActivityUpdates(IUserActivityListener l) {
		this.listeners.add(l);
	}

	@Override
	public void onProviderDisabled(String provider) {
		if (this.provider == provider) {
		}
		
	}

	@Override
	public void onProviderEnabled(String provider) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onStatusChanged(String provider, int status, Bundle extras) {
		// TODO Auto-generated method stub
	}
	
	private ILogger logger;
	public void log(ILogger logger) {
		this.logger = logger;
	}
	
	private void log(Location l) {
		if (this.logger != null && l != null) {
			this.logger.log(l);
		}
	}
}
