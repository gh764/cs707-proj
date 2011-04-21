package edu.wisc.cs707.io;

import edu.wisc.cs707.src.ModelInfo;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.src.PointsOfInterest;
import edu.wisc.cs707.util.LocationController;

public interface IStorageHandler {

	public PointsOfInterest loadPointsOfInterest(); 
	public void save(PointOfInterest p);
	
	public void save(LocationController.Snapshot snapshot);
	
	public ModelInfo loadModelInfo();
}
