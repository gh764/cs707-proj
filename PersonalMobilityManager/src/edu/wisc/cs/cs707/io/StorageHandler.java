package edu.wisc.cs.cs707.io;

import java.io.EOFException;
import java.io.FileNotFoundException;
import java.util.Date;

import android.content.Context;
import edu.wisc.cs707.src.ModelInfo;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.src.PointsOfInterest;
import edu.wisc.cs707.util.LocationController.Snapshot;

public class StorageHandler implements IStorageHandler {

	private static StorageHandler instance;
	
	private DatabaseHandler dbHandler = null;
	private DataFileStorageHandler dfsHandler = null;
	
	private StorageHandler(Context context) {
		this.dbHandler = new DatabaseHandler(context);
		this.dfsHandler = new DataFileStorageHandler(context);
	}
	
	public static StorageHandler getInstance(Context context) {
		if (instance == null)
			return instance = new StorageHandler(context);
		return instance;
	}
	
	@Override
	public PointsOfInterest loadPointsOfInterest() {
		return this.dbHandler.loadPointsOfInterest();
	}

	@Override
	public void save(PointOfInterest poi) {
		this.dbHandler.save(poi);
	}

	@Override
	public void save(Snapshot snapshot) {
		this.dbHandler.save(snapshot);
	}

	@Override
	public ModelInfo loadModelInfo() {
		
		boolean create = true;
		
		try {
			return this.dfsHandler.loadModelInfo();
		} catch (FileNotFoundException e) {
			create = true;
		} catch (EOFException e) {
			create = true;
		} finally {
			if (create) {
				ModelInfo info = new ModelInfo(1, 1, new Date());
				info.setDateUpdated(new Date());
				if (this.dfsHandler.save(info)) {
					return info;
				} else {
					return null;
				}
			}
		}
		
		return null;
	}

	
	
}
