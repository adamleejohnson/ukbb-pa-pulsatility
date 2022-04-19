# Manuel A. Morales (moralesq@mit.edu)
# Harvard-MIT Department of Health Sciences & Technology  
# Athinoula A. Martinos Center for Biomedical Imaging

#/*=========================================================================
# This file is a python implementation of: 
# https://github.com/horosproject/horos/blob/8cf32ca079363109a3871d24f4013fd704992dfe/Horos/Sources/ROI.m

import re
import numpy as np

def spline(coords, scale):
    
    if scale > 5: scale=5
    
    tot = len(coords)
    
    nb  = tot + 2
    scale = 5
    
    a   = np.zeros(nb)
    c   = np.zeros(nb)
    cx  = np.zeros(nb)
    cy  = np.zeros(nb)
    d   = np.zeros(nb)
    g   = np.zeros(nb)
    gam = np.zeros(nb)
    h   = np.zeros(nb)
    px  = np.zeros(nb)
    py  = np.zeros(nb)
    
    # as a spline starts and ends with a line one adds two points
    # in order to have continuity in starting point
    for i in range(tot):
        px[i+1] += coords[i,0]
        py[i+1] += coords[i,1]

    px[0] = px[nb-2]; px[nb-1] = px[1]
    py[0] = py[nb-2]; py[nb-1] = py[1]
    #px[0] = px[nb-3]; px[nb-1] = px[2]
    #py[0] = py[nb-3]; py[nb-1] = py[2]
    
    # check all points are separate, if not do not smooth
    # this happens when the zoom factor is too small
    # so in this case the smooth is not useful
    for i in range(1, nb): assert not (px[i] == px[i-1])&(py[i] == py[i-1])
        
    # define hi (distance between points) h0 distance between 0 and 1.
    # di distance of point i from start point
    for i in range(nb-1):
        xi = px[i+1] - px[i];
        yi = py[i+1] - py[i];
        h[i] = np.sqrt(xi*xi + yi*yi) * scale;
        d[i+1] = d[i] + h[i];
        
    # define ai and ci
    for i in range(2, nb-1): a[i] = 2.0 * h[i-1] / (h[i] + h[i-1]);
    for i in range(1, nb-2): c[i] = 2.0 * h[i] / (h[i] + h[i-1]);
        
        
    # define gi in function of x
    # gi+1 = 6 * Y[hi, hi+1, hi+2], 
    # Y[hi, hi+1, hi+2] = [(yi - yi+1)/(di - di+1) - (yi+1 - yi+2)/(di+1 - di+2)]
    #                      / (di - di+2)

    for i in range(1, nb-1):
        g[i] = 6.0 * ( ((px[i-1] - px[i]) / (d[i-1] - d[i])) - ((px[i] - px[i+1]) / (d[i] - d[i+1])) ) / (d[i-1]-d[i+1]);

    # compute cx vector
    b=4; bet=4;
    cx[1] = g[1]/b;
    for j in range(2, nb-1):

        gam[j] = c[j-1] / bet;
        bet = b - a[j] * gam[j];
        cx[j] = (g[j] - a[j] * cx[j-1]) / bet;

    for j in range(nb-2, 0, -1): cx[j] -= gam[j+1] * cx[j+1];

    # define gi in function of y
    # gi+1 = 6 * Y[hi, hi+1, hi+2], 
    # Y[hi, hi+1, hi+2] = [(yi - yi+1)/(hi - hi+1) - (yi+1 - yi+2)/(hi+1 - hi+2)]
    #                      / (hi - hi+2)


    for i in range(1, nb-1):
        g[i] = 6.0 * ( ((py[i-1] - py[i]) / (d[i-1] - d[i])) - ((py[i] - py[i+1]) / (d[i] - d[i+1])) ) / (d[i-1]-d[i+1]);

    # compute cy vector
    b = 4.0; bet = 4.0;
    cy[1] = g[1] / b;

    for j in range(2, nb-1):

        gam[j] = c[j-1] / bet;
        bet = b - a[j] * gam[j];
        cy[j] = (g[j] - a[j] * cy[j-1]) / bet;


    for j in range(nb-2, 0, -1): cy[j] -= gam[j+1] * cy[j+1];

        
    # OK we have the cx and cy vectors, from that we can compute the
    # coeff of the polynoms for x and y and for each interval
    # S(x) (xi, xi+1)  = ai + bi (x-xi) + ci (x-xi)2 + di (x-xi)3
    # di = (ci+1 - ci) / 3 hi
    # ai = yi
    # bi = ((ai+1 - ai) / hi) - (hi/3) (ci+1 + 2 ci)

    totNewPt = 0;
    for i in range(0, nb-2):
        totNewPt += 1

        for j in range(1, int(np.floor(h[i]))+1): totNewPt += 1

    newPt = np.zeros((totNewPt,2))       
    tt = 0
    for i in range(0, nb-2):
        # compute coef for x polynom
        ccx = cx[i];
        aax = px[i];
        ddx = (cx[i+1] - cx[i]) / (3.0 * h[i]);
        bbx = ((px[i+1] - px[i]) / h[i]) - (h[i] / 3.0) * (cx[i+1] + 2.0 * cx[i]);

        # compute coef for y polynom
        ccy = cy[i];
        aay = py[i];
        ddy = (cy[i+1] - cy[i]) / (3.0 * h[i]);
        bby = ((py[i+1] - py[i]) / h[i]) - (h[i] / 3.0) * (cy[i+1] + 2.0 * cy[i]);

        newPt[tt,0] = aax
        newPt[tt,1] = aay

        tt += 1

        for j in range(1, int(np.floor(h[i]))+1):
            newPt[tt,0] = aax + bbx * j + ccx * j * j + ddx * j * j * j;
            newPt[tt,1] = aay + bby * j + ccy * j * j + ddy * j * j * j;

            tt += 1    
            
    return newPt-0.5

def decode_NS(NS, apply_spline=True):
    
    if re.search('{.*,.*}', NS) is None: return np.nan, np.nan
    points  = re.search('{.*,.*}', NS).group().split('\\')
    contour = [np.array(points[0].strip('{}').split(','), dtype=float)]
    for point in points:
        if point.startswith('x9a'):
            try:
                 contour += [np.array(re.search('{.*,.*}', point).group().strip('{}').split(','), dtype=float)]
            except:
                continue
        elif point.startswith('x10'): break
    
    if 'Area' in NS:
        area_cm2 = float(NS.split('Area')[1].split('\\')[0].strip(': cm'))
    else:
        area_cm2 = np.nan
        
    contour  = np.stack(contour,0)
    
    if apply_spline: contour = spline(contour, scale=1)
        
    # close the contour is needed to transform to mask later. 
    closed_contour = np.concatenate((contour, contour[:1]))
    
    return closed_contour, area_cm2