package edu.wisc.cs707.util;

import android.location.Location;
import edu.wisc.cs707.util.LocationController.Snapshot;

public interface ILogger {

	public void log(Snapshot snapshot);
	public void log(Location location);
	public void log(String caption, String text);
	public void log(Object o);
}
