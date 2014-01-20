package smarthome.server.data;

import smarthome.server.Base16;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity
public class Snapshot {

    @Id
    private Long timestamp;

    private byte[] value;

    public Snapshot() {
    }

    public Snapshot(long timestamp, byte[] value) {
        this.timestamp = timestamp;
        this.value = value;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public byte[] getValue() {
        return value;
    }

    public void setValue(byte[] value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return String.format("%016x: %s", timestamp, Base16.encode(value));
    }
}
