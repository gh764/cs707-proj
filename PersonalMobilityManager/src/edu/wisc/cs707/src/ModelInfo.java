package edu.wisc.cs707.src;

import java.io.Serializable;
import java.util.Calendar;
import java.util.Date;

public class ModelInfo implements Serializable {

	public static final int TOTAL_MISMATCH_TRIGGER = 0;
	public static final int STREAK_MISMATCH_TRIGGER = 1;
	public static final int LAST10_MISMATCH_TRIGGER = 2;
	
	private class ModelStatistics implements Serializable {

		private static final long serialVersionUID = 3446766253135834424L;
		
		int nrMatches = 0;
		int nrSuccessful = 0;
		int streak = 0;
		int [] last10 = new int[10]; // (total << 16) + matched
	}
	
	private class ModelTriggers implements Serializable {
		private static final long serialVersionUID = -2647006913280430405L;
		float [] settings = new float[] {0.5f, 5f, 0.5f};
	}
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public enum Schedule {
		REGULAR,
		IRREGULAR;
	};
	
	public enum AggregrateFunction {
		ARITHMETIC_AVERAGE,
		WEIGHTED_AVERAGE;
	}
	
	private int id;
	private int version;
	private Schedule schedule = Schedule.REGULAR;
	private Date dateCreated;
	private Date dateUpdated;
	
	private int staleAfter = 90;
	private int earliestRebuild = 7;
	
	private int windowSize = 90;
	private AggregrateFunction aggFx = AggregrateFunction.ARITHMETIC_AVERAGE;
	private int granularity = 3;
	
	private ModelStatistics statistics = new ModelStatistics();
	private ModelTriggers triggers = new ModelTriggers();
	
	private boolean rebuild = false;
	
	public ModelInfo(int id, int version, Date dateCreated) {
		this.id = id;
		this.version = version;
		this.dateCreated = dateCreated;
	}

	public int getVersion() {
		return version;
	}

	public void setVersion(int version) {
		this.version = version;
	}

	public Schedule getSchedule() {
		return schedule;
	}

	public void setSchedule(Schedule schedule) {
		this.schedule = schedule;
	}

	public Date getDateUpdated() {
		return dateUpdated;
	}

	public void setDateUpdated(Date dateUpdated) {
		this.dateUpdated = dateUpdated;
	}

	public int getStaleAfter() {
		return staleAfter;
	}

	public void setStaleAfter(int staleAfter) {
		this.staleAfter = staleAfter;
	}

	public int getEarliestRebuild() {
		return earliestRebuild;
	}

	public void setEarliestRebuild(int earliestRebuild) {
		this.earliestRebuild = earliestRebuild;
	}

	public int getWindowSize() {
		return windowSize;
	}

	public void setWindowSize(int windowSize) {
		this.windowSize = windowSize;
	}

	public AggregrateFunction getAggFx() {
		return aggFx;
	}

	public void setAggFx(AggregrateFunction aggFx) {
		this.aggFx = aggFx;
	}

	public int getGranularity() {
		return granularity;
	}

	public void setGranularity(int granularity) {
		this.granularity = granularity;
	}
	
	public int getUpdateFrequency() {
		return this.granularity;
	}

	public int getNrMatches() {
		return this.statistics.nrMatches;
	}

	public void setNrMatches(int nrMatches) {
		this.statistics.nrMatches = nrMatches;
	}

	public int getNrSuccessful() {
		return this.statistics.nrSuccessful;
	}

	public void setNrSuccessful(int nrSuccessful) {
		this.statistics.nrSuccessful = nrSuccessful;
	}

	public int getStreak() {
		return this.statistics.streak;
	}

	public void setStreak(int streak) {
		this.statistics.streak = streak;
	}
	
	private int getLast10X(int mask, int rshift) {
		int total = 0;
		for (int i = 0; i < 10; i++) {
			total += ((this.statistics.last10[i] & mask) >> rshift);
		}
		
		return total;
	}

	public int getLast10NrSuccessful() {
		return this.getLast10X(0xffff, 0);
	}
	
	public int getLast10NrMatches() {
		return this.getLast10X(0xffff0000, 16);
	}

	public boolean isRebuild() {
		return rebuild;
	}

	public void setRebuild(boolean rebuild) {
		this.rebuild = rebuild;
	}
	
	public float getTrigger(int trigger) {
		return this.triggers.settings[trigger];
	}
	
	public void setTrigger(int trigger, float value) {
		this.triggers.settings[trigger] = value;
	}

	public int getId() {
		return id;
	}

	public Date getDateCreated() {
		return dateCreated;
	}
	
	public Date getExpDate() {
		Calendar c1 = Calendar.getInstance();
		
		c1.set(this.dateUpdated.getYear(), this.dateUpdated.getMonth(),
				this.dateUpdated.getDate());
		
		c1.add(Calendar.DATE, this.staleAfter);
		
		return new Date(c1.get(Calendar.YEAR) - 1900,
				c1.get(Calendar.MONTH) - 1, c1.get(Calendar.DATE));
	}
}
