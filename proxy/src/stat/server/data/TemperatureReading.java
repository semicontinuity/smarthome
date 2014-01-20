package stat.server.data;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity
public class TemperatureReading {

    @Id
    private Long timestamp;

    private float value;

    public TemperatureReading() {
    }

    public TemperatureReading(long timestamp, float value) {
        this.timestamp = timestamp;
        this.value = value;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public float getValue() {
        return value;
    }

    public void setValue(float value) {
        this.value = value;
    }
}
