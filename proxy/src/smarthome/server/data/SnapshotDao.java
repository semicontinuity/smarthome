package smarthome.server.data;


import javax.persistence.EntityManager;
import javax.persistence.Query;
import java.util.List;

public enum SnapshotDao {
    INSTANCE;

    @SuppressWarnings("UnusedDeclaration")
    public List<Snapshot> findAll() {
        final EntityManager em = EMFService.get().createEntityManager();
        final Query q = em.createQuery("select s from Snapshot s");
        final List resultList = q.getResultList();
        em.close();
        //noinspection unchecked
        return resultList;
    }

    public void add(final List<Snapshot> snapshots) {
        final EntityManager em = EMFService.get().createEntityManager();
        for (Snapshot snapshot : snapshots) {
            em.persist(snapshot);
        }
        em.close();
    }
}
