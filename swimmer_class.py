# -*- coding: utf-8 -*-
"""Module for the Swimmer class and its methods."""

import numpy as np
from functions_general import panel_vectors, archive
from swimmer_subclasses import Body, Edge, Wake

class Swimmer(object):
    """A single swimmer, consisting of Body, Edge, and Wake objects.

    Currently the swimmer is made of a single Body, Edge, and Wake. Separation
    occurs at the trailing edge only, hence the single Edge and single Wake
    behind it. In the future this class will likely need to possess multiple
    Edges where separation occurs, so the methods would have to be
    changed accordingly.

    Attributes:
        CE: Constant that determines the length of Edge panels.
        DELTA_CORE: Constant used in wake_rollup to avoid singularities near
            wake panels.
        SW_GEOMETRY: Switch for Body geometry type (currently VDV only).
        SW_KUTTA: Switch for Kutta condition (explicit or unsteady).
        SW_WAKE: Switch for wake type (doublet sheets or vortex particles).
        V0: Free-stream velocity.
    """
    def __init__(self, SwimmerParameters, GeoParameters, MotionParameters, COUNTER):
        """Inits Swimmer with all necessary parameters.

        This is also where Body, Edge, and Wake are created.
        GeoParameters and MotionParameters get passed along into Body creation.
        """
        self.V0 = MotionParameters.V0
        self.CE = SwimmerParameters.CE
        self.DELTA_CORE = SwimmerParameters.DELTA_CORE
        self.SW_KUTTA = SwimmerParameters.SW_KUTTA

#       TODO: Create new 3D Geometries and add them here
        if GeoParameters.SW_GEOMETRY == 'VDV':
            self.Body = Body.from_van_de_vooren(GeoParameters, MotionParameters)

        if GeoParameters.SW_GEOMETRY == 'FP':
            self.Body = Body.flat_plate(GeoParameters, MotionParameters)

        if GeoParameters.SW_GEOMETRY == 'TD':
            self.Body = Body.tear_drop(GeoParameters, MotionParameters)

        self.Edge = Edge(self.CE)
        self.Wake = Wake(COUNTER)

    def edge_shed(self, DEL_T, i):
        """Updates the position of the Edge panel.

        This should only be done once each time step for a swimmer.
        The edge panel's length is based on Edge.CE.
        The strength of this panel is solved for in kutta().

        Args:
            DEL_T: Time step length.
            i: Time step number.
            Body: Body of the swimmer.
            Edge: Edge panel of separation.
        """
        Body = self.Body
        Edge = self.Edge

        tx = panel_vectors(Body.AF.x_neut, Body.AF.z_neut)[0][0]
        tz = panel_vectors(Body.AF.x_neut, Body.AF.z_neut)[1][0]

        Edge.x[0] = Body.AF.x[0]
        Edge.z[0] = Body.AF.z[0]
        Edge.x[1] = Edge.x[0] + Edge.CE*tx*Body.V0*DEL_T
        Edge.z[1] = Edge.z[0] + Edge.CE*tz*Body.V0*DEL_T

    def wake_shed(self, DEL_T, i):
        """Updates the positions of the Wake panels.

        This should only be done once each time step for a swimmer.

        Args:
            DEL_T: Time step length.
            i: Time step number.
            Edge: Edge panel of separation.
            Wake: Wake panels.
            V0: Free-stream velocity.
        """
        Edge = self.Edge
        Wake = self.Wake
        V0 = self.V0

        if i == 0:
            pass

        elif i == 1:
            # Initialize wake coordinates
            Wake.x[0] = Edge.x[-1]
            Wake.z[0] = Edge.z[-1]

            Wake.x[1:] = Wake.x[0] + np.arange(1,np.size(Wake.x))*(-V0)*DEL_T
            Wake.z[1:] = Wake.z[0]

        elif i > 1:
            archive(Wake.x)
            archive(Wake.z)
            archive(Wake.mu)

            Wake.x[0] = Edge.x[-1]
            Wake.z[0] = Edge.z[-1]
            Wake.mu[0] = Edge.mu

            Wake.gamma[0] = -Wake.mu[0]
            Wake.gamma[1:-1] = Wake.mu[:-1]-Wake.mu[1:]
            Wake.gamma[-1] = Wake.mu[-1]