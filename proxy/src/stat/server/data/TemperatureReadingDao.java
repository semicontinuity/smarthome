package stat.server.data;


import javax.persistence.EntityManager;
import javax.persistence.Query;
import java.util.List;

public enum TemperatureReadingDao {
    INSTANCE;

    @SuppressWarnings("UnusedDeclaration")
    public List<TemperatureReading> findAll() {
        final EntityManager em = EMFService.get().createEntityManager();
        final Query q = em.createQuery("select r from TemperatureReading r");
        final List resultList = q.getResultList();
        em.close();
        //noinspection unchecked
        return resultList;
    }

    public List<TemperatureReading> findLatest() {
        final EntityManager em = EMFService.get().createEntityManager();
        final Query q = em.createQuery("select r from TemperatureReading r where r.timestamp > :start");
        final List resultList = q.setParameter("start", System.currentTimeMillis() - 86400000L).getResultList();
        em.close();
        //noinspection unchecked
        return resultList;
    }

    public void add(final long timestamp, final float value) {
        final EntityManager em = EMFService.get().createEntityManager();
        final TemperatureReading temperatureReading = new TemperatureReading(timestamp, value);
        em.persist(temperatureReading);
        em.close();
    }
}
