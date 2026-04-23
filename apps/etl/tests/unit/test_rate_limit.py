import time

from olho_publico_etl.sources.transparencia.rate_limit import TokenBucket


def test_bucket_permite_burst_inicial():
    bucket = TokenBucket(rate_per_minute=60, capacity=60)
    for _ in range(10):
        assert bucket.try_acquire() is True


def test_bucket_bloqueia_quando_vazio():
    bucket = TokenBucket(rate_per_minute=60, capacity=2)
    bucket.try_acquire()
    bucket.try_acquire()
    assert bucket.try_acquire() is False


def test_bucket_reenche_com_o_tempo():
    bucket = TokenBucket(rate_per_minute=6000, capacity=1)  # 100/s
    bucket.try_acquire()
    assert bucket.try_acquire() is False
    time.sleep(0.03)  # 30ms = ~3 tokens
    assert bucket.try_acquire() is True


def test_bucket_acquire_bloqueante_espera():
    bucket = TokenBucket(rate_per_minute=6000, capacity=1)
    bucket.try_acquire()
    t0 = time.monotonic()
    bucket.acquire()  # bloqueia ~10ms (1 token em 100/s)
    elapsed = time.monotonic() - t0
    assert 0.005 < elapsed < 0.1
