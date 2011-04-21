package edu.wisc.cs707.util;

public interface IUserActivityListener {

	public void onUserActivityUpdate(LocationController.Activity activity, LocationController.Snapshot snapshot);
}