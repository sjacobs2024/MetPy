from numpy.testing import *
import numpy as np
from metpy.calc import *
from metpy.constants import g

class TestVaporPressure(TestCase):
    def test_basic(self):
        temp = np.array([5, 10, 18, 25])
        real_es = np.array([8.72, 12.28, 20.64, 31.68])
        assert_array_almost_equal(vapor_pressure(temp), real_es, 2)

    def test_scalar(self):
        es = vapor_pressure(0)
        assert_almost_equal(es, 6.112, 3)

class TestDewpoint(TestCase):
    def test_basic(self):
        temp = np.array([30, 25, 10, 20, 25])
        rh = np.array([30, 45, 55, 80, 85])/100.

        real_td = np.array([11, 12, 1, 16, 22])
        assert_array_almost_equal(real_td, dewpoint(temp, rh), 0)

    def test_scalar(self):
        td = dewpoint(10.6, .37) * 1.8 + 32.
        assert_almost_equal(td, 26, 0)

class TestWindComps(TestCase):
    def test_basic(self):
        'Test the basic calculation.'
        speed = np.array([4, 4, 4, 4, 25, 25, 25, 25, 10.])
        dirs = np.array([0, 45, 90, 135, 180, 225, 270, 315, 360])
        s2 = np.sqrt(2)

        u,v = get_wind_components(speed, dirs)

        true_u = np.array([0, -4/s2, -4, -4/s2, 0, 25/s2, 25, 25/s2, 0])
        true_v = np.array([-4, -4/s2, 0, 4/s2, 25, 25/s2, 0, -25/s2, -10])

        assert_array_almost_equal(true_u, u, 4)
        assert_array_almost_equal(true_v, v, 4)

    def test_scalar(self):
        comps = np.array(get_wind_components(8, 150))
        assert_array_almost_equal(comps, np.array([-4, 6.9282]), 3)

class TestWindChill(TestCase):
    def test_basic(self):
        'Test the basic wind chill calculation.'
        temp = np.array([40, -10, -45, 20])
        speed = np.array([5, 55, 25, 15])

        wc = windchill(temp, speed, metric=False)
        values = np.array([36, -46, -84, 6])
        assert_array_almost_equal(wc, values, 0)

    def test_scalar(self):
        wc = windchill(-5, 35, metric=False)
        assert_almost_equal(wc, -34, 0)

    def test_metric(self):
        'Test the basic wind chill calculation.'
        temp = (np.array([40, -10, -45, 20]) - 32.) / 1.8
        speed = np.array([5, 55, 25, 15]) * .44704

        wc = windchill(temp, speed, metric=True)
        values = (np.array([36, -46, -84, 6]) - 32.) / 1.8
        assert_array_almost_equal(wc, values, 0)

    def test_invalid(self):
        'Test for values that should be masked.'
        temp = np.array([50, 51, 49, 60, 80, 81])
        speed = np.array([4, 4, 3, 1, 10, 39])

        wc = windchill(temp, speed, metric=False)
        mask = np.array([False, True, True, True, True, True])
        assert_array_equal(wc.mask, mask)

    def test_undefined_flag(self):
        'Tests whether masking values can be disabled.'
        temp = np.ma.array([49, 50, 49, 60, 80, 81])
        speed = np.ma.array([4, 4, 3, 1, 10, 39])

        wc = windchill(temp, speed, metric=False, mask_undefined=False)
        mask = np.array([False]*6)
        assert_array_equal(wc.mask, mask)

class TestHeatIndex(TestCase):
    def test_basic(self):
        'Test the basic heat index calculation.'
        temp = np.array([80, 88, 92, 110])
        rh = np.array([40, 100, 70, 40])

        hi = heat_index(temp, rh)
        values = np.array([80, 121, 112, 136])
        assert_array_almost_equal(hi, values, 0)

    def test_scalar(self):
        hi = heat_index(96, 65)
        assert_almost_equal(hi, 121, 0)

    def test_invalid(self):
        'Test for values that should be masked.'
        temp = np.array([80, 88, 92, 79, 30, 81])
        rh = np.array([40, 39, 2, 70, 50, 39])

        hi = heat_index(temp, rh)
        mask = np.array([False, True, True, True, True, True])
        assert_array_equal(hi.mask, mask)

    def test_undefined_flag(self):
        'Tests whether masking values can be disabled.'
        temp = np.ma.array([80, 88, 92, 79, 30, 81])
        rh = np.ma.array([40, 39, 2, 70, 50, 39])

        hi = heat_index(temp, rh, mask_undefined=False)
        mask = np.array([False]*6)
        assert_array_equal(hi.mask, mask)

#class TestIrrad(TestCase):
#    def test_basic(self):
#        'Test the basic solar irradiance calculation.'
#        from datetime import date

#        d = date(2008, 9, 28)
#        lat = 35.25
#        hours = np.linspace(6,18,10)

#        s = solar_irradiance(lat, d, hours)
#        values = np.array([0., 344.1, 682.6, 933.9, 1067.6, 1067.6, 933.9,
#            682.6, 344.1, 0.])
#        assert_array_almost_equal(s, values, 1)

#    def test_scalar(self):
#        from datetime import date
#        d = date(2008, 9, 28)
#        lat = 35.25
#        hour = 9.5
#        s = solar_irradiance(lat, d, hour)
#        assert_almost_equal(s, 852.1, 1)

#    def test_invalid(self):
#        'Test for values that should be masked.'
#        from datetime import date
#        d = date(2008, 9, 28)
#        lat = 35.25
#        hours = np.linspace(0,22,12)
#        s = solar_irradiance(lat, d, hours)

#        mask = np.array([ True,  True,  True,  True, False, False, False,
#            False, False, True,  True,  True])
#        assert_array_equal(s.mask, mask)

class TestGradients(TestCase):
    def test_basic(self):
        'Basic braindead test of vorticity and divergence calculation'
        u = np.ones((3,3))
        c,v = convergence_vorticity(u, u, 1, 1)
        truth = np.zeros_like(u)
        assert_array_equal(c, truth)
        assert_array_equal(v, truth)

    def test_basic2(self):
        'Basic test of vorticity and divergence calculation'
        a = np.arange(3)
        u = np.c_[a, a, a]
        c,v = convergence_vorticity(u, u.T, 1, 1)
        true_c = 2. * np.ones_like(u)
        true_v = np.zeros_like(u)
        assert_array_equal(c, true_c)
        assert_array_equal(v, true_v)

    def test_basic3(self):
        'Basic test of vorticity and divergence calculation'
        a = np.arange(3)
        u = np.c_[a, a, a]
        c,v = convergence_vorticity(u, u, 1, 1)
        true_c = np.ones_like(u)
        true_v = np.ones_like(u)
        assert_array_equal(c, true_c)
        assert_array_equal(v, true_v)

class TestAdvection(TestCase):
    def test_basic(self):
        'Basic braindead test of advection'
        u = np.ones((3,))
        s = np.ones_like(u)
        a = advection(s, u, (1,))
        truth = np.zeros_like(u)
        assert_array_equal(a, truth)

    def test_basic2(self):
        'Basic test of advection'
        u = np.ones((3,))
        s = np.array([1, 2, 3])
        a = advection(s, u, (1,))
        truth = -np.ones_like(u)
        assert_array_equal(a, truth)

    def test_basic3(self):
        'Basic test of advection'
        u = np.array([1, 2, 3])
        s = np.array([1, 2, 3])
        a = advection(s, u, (1,))
        truth = np.array([-1, -2, -3])
        assert_array_equal(a, truth)

    def test_2dbasic(self):
        'Basic 2D braindead test of advection'
        u = np.ones((3,3))
        v = np.ones((3,3))
        s = np.ones_like(u)
        a = advection(s, u, (1,))
        truth = np.zeros_like(u)
        assert_array_equal(a, truth)

    def test_2dbasic2(self):
        'Basic 2D test of advection'
        u = np.ones((3,3))
        v = 2 * np.ones((3,3))
        s = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
        a = advection(s, [u, v], (1, 1))
        truth = np.array([[-3, -2, 1], [-4, 0, 4], [-1, 2, 3]])
        assert_array_equal(a, truth)

class TestGeos(TestCase):
    def test_basic(self):
        'Basic test of geostrophic wind calculation'
        z = np.array([[48, 49, 48], [49, 50, 49], [48, 49, 48]]) * 100.
        #Using g as the value for f allows it to cancel out
        ug, vg = geostrophic_wind(z, g, 100., 100.)
        true_u = np.array([[-1, 0, 1]]*3)
        true_v = -true_u.T
        assert_array_equal(ug, true_u)
        assert_array_equal(vg, true_v)

if __name__ == '__main__':
    run_module_suite()
