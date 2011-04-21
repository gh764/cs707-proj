package edu.wisc.cs707.src;

import java.io.Serializable;
import java.text.DecimalFormat;

import android.location.Location;

public class PointOfInterest implements Serializable {

	private static final long serialVersionUID = 3246027485698566355L;
	
	private int id;
	private String name;
	private double latitude;
	private double longitude;
	private int altitude;
	private int radius;
	private boolean monitored = true;
	
	public PointOfInterest() {
		this(-1, "New Location", 0, 0, 0, false);
	}
	
	public PointOfInterest(int id, String name, double latitude, double longitude, int radius) {
		this(id, name, latitude, longitude, radius, 0, true);
	}
	
	public PointOfInterest(int id, String name, double latitude, double longitude, 
			int radius, boolean monitored) {
		this(id, name, latitude, longitude, radius, 0, monitored);
	}
	
	public PointOfInterest(int id, String name, double latitude, double longitude, 
			int radius, int altitude) {
		this(id, name, latitude, longitude, radius, altitude, true);
	}
	
	public PointOfInterest(int id, String name, double latitude, double longitude, 
			int radius, int altitude, boolean monitored) {
		this.id = id;
		this.name = name;
		this.longitude = longitude;
		this.latitude = latitude;
		this.radius = radius;
		this.altitude = altitude;
		this.monitored = monitored;
	}
	
	public PointOfInterest(PointOfInterest other) {
		this.assign(other);
	}
	
	private static PointOfInterest unspecified = new PointOfInterest(0, "<Unspecified>", 0, 0, 0, 0);
	public static PointOfInterest Unspecified() {
		return unspecified;
	}
	
	public boolean contains(double latitude, double longitude) {
		return this.contains(latitude, longitude, 0);
	}
	
	public boolean contains(double latitiude, double longitude, int accuracy) {
		float [] results = new float[1];
		Location.distanceBetween(this.latitude, this.longitude, latitude, longitude, results);
		return results[0] <= this.radius + accuracy;
	}
	
	/**
	 * @return the id
	 */
	public int getId() {
		return id;
	}

	/**
	 * @param id the id to set
	 */
	public void setId(int id) {
		this.id = id;
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}

	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * @return the latitude
	 */
	public double getLatitude() {
		return latitude;
	}

	/**
	 * @param latitude the latitude to set
	 */
	public void setLatitude(double latitude) {
		this.latitude = latitude;
	}

	/**
	 * @return the longitude
	 */
	public double getLongitude() {
		return longitude;
	}

	/**
	 * @param longitude the longitude to set
	 */
	public void setLongitude(double longitude) {
		this.longitude = longitude;
	}

	/**
	 * @return the altitude
	 */
	public int getAltitude() {
		return altitude;
	}

	/**
	 * @param altitude the altitude to set
	 */
	public void setAltitude(int altitude) {
		this.altitude = altitude;
	}

	/**
	 * @return the radius
	 */
	public int getRadius() {
		return radius;
	}

	/**
	 * @param radius the radius to set
	 */
	public void setRadius(int radius) {
		this.radius = radius;
	}

	/**
	 * @return the monitored
	 */
	public boolean isMonitored() {
		return monitored;
	}

	/**
	 * @param monitored the monitored to set
	 */
	public void setMonitored(boolean monitored) {
		this.monitored = monitored;
	}

	public String toString() {
		return this.name;
	}
	
	public String toString(boolean verbose) {
		if (verbose) {
			DecimalFormat df = new DecimalFormat("#.##");
			return this.name + "[id=" + this.id + ";lat="  + df.format(this.latitude) +
				";long=" + df.format(this.longitude) + ";rad=" + this.radius + ";alt=" + this.altitude + 
				";monitor=" + this.monitored + "]";
		} else {
			return this.name + "[id=" + this.id + "]";
		}
	}
	
	public PointOfInterest assign(PointOfInterest other) {
		this.id = other.id;
		this.name = other.name;
		this.longitude = other.longitude;
		this.latitude = other.latitude;
		this.radius = other.radius;
		this.altitude = other.altitude;
		this.monitored = other.monitored;
		
		return this;
	}
}
