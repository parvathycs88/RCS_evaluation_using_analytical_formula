import scipy.optimize as opt
import numpy as np
import math
import keras
from keras.models import load_model
import pandas as pd
import time
import matplotlib.pyplot as plt

pi = np.pi

theta_= np.linspace(0,pi/2,90)
phi_= np.linspace(0,2*pi,360)
theta,phi = np.meshgrid(theta_,phi_) # Makind 2D grid

df_v1 = pd.read_excel('Selected_frequency_ReflectionPhase_1_openingangle_10_length_6.xlsx') # dimensions of '0'th element V1
df_v2 = pd.read_excel('Selected_frequency_ReflectionPhase_1_openingangle_85_length_10.xlsx') # dimensions of '0'th element V2
#lambda0 = pd.DataFrame([])
#lambda0 = (3*10^8)/(df_v1["frequency"])
#k = 2*pi/lambda0
D = .03 #Half of Center frequency lambda
#omsriramajayam

N = 10 # 10 by 10 array of 2 different v-shaped element
df = pd.DataFrame([])
df1 = pd.DataFrame([])

result = []

df_v1["reflectionphase_unwrapped"] = np.deg2rad(df_v1["reflectionphase"]) #np.unwrap((np.deg2rad(df_v1["reflectionphase"])) %2*np.pi) # modulo 2*pi helps to change range from -pi to +pi to 0 to 2*pi  
df_v2["reflectionphase_unwrapped"] = np.deg2rad(df_v2["reflectionphase"])#np.unwrap((np.deg2rad(df_v2["reflectionphase"])) %2*np.pi)  
df_v2["frequency"] = df_v2["frequency"] *10**9
def fun(x,i):
    #L_v = x[:N**2]#np.unwrap(np.deg2rad(df_v2["reflectionphase"]))
    #theta_v = x[N**2:]
    phase_pred = []
    for element in x.ravel():
        if(element == 0):
            phase_pred.append(df_v1["reflectionphase_unwrapped"][i])
            
        else:
            phase_pred.append(df_v2["reflectionphase_unwrapped"][i])  
              
    #df_v1["frequency"][i] = df_v1["frequency"][i].apply(lambda x:x*1.0*10^9)
    lambda0 = (3*10**8)/(df_v2["frequency"][i]) # 3*10^8/10^9 for  GHz
    #D = lambda0
    k = 2*pi/lambda0
    #for t,l in zip(theta_v,L_v):
        #if((t == 0) & (l == 0)):
            #phase_pred.append(df_v1["reflectionphase_unwrapped"][i])
        #if((t == 1) & (l == 1)):
            #phase_pred.append(df_v2["reflectionphase_unwrapped"][i])   
    
        #omsriramajayam
    reflection_phase = np.reshape(phase_pred, (N,N))
    print(reflection_phase)
    #omsriramajayam
   
    S = 0
    for m in range(N):
        for n in range(N): 
            #u=phase_pred(1,(m-1)*N+n)   
            S2 =  np.exp(-1j * (reflection_phase[m,n] + k*D*np.sin(theta)*((m-1/2)*np.cos(phi)+((n-1/2)*np.sin(phi)))))
            S = S + S2
            
    S = np.cos(theta) * S  
    H = np.trapz(np.trapz(np.abs(S)**2*np.sin(theta),theta_),phi_) # integration using trapezoid function
    directivity = (4 * pi * np.abs(S)**2) / (H)
    rcs = (lambda0**2 * np.max(directivity))/(4*pi*(N**2)*(D**2))
    rcs_dB = 10 * np.log10(rcs) 
    return rcs_dB
#omsriramajayam

#dataframe = pd.read_excel('Length_Openingangle_V_Elements_Pattern_Design.xlsx')
state_list = []  

#frequency_list = np.arange(6.0,14.1,0.5) 
number_of_frequency_points = len(df_v1)

number_of_combinations = 1#10
x = np.zeros((number_of_combinations,100))  #Initialise numpy array x

rcs_over_frequency = {} #pd.DataFrame([])
list_of_rcs_over_frequency = pd.DataFrame([])
#frac_list = [0.05,0.16,0.28,0.32,0.44,0.53,0.61,0.72,0.87,0.97]#for binomial distribution
#frac_list_2 = [0.01,0.12,0.23,0.37,0.49,0.57,0.68,0.76,0.82,0.91]
frac_list_3 = [0.00]
for times in range(number_of_combinations):#(dataframe.shape[0]):# number of instances
    state = np.random.binomial(1, frac_list_3[times], size=100)
    #state = np.append([np.zeros(50)],[np.ones(50)])  
    #state = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
    for i in range(number_of_frequency_points):
        x[times] = state #np.array((t,l)).ravel() 
        #x[times][N**2:] = state
        #x[times] = state
        rcs_over_frequency['Combination_number_%d_%%d' %times %i] = fun(x[times],i)
        list_of_rcs_over_frequency.loc['%d' %times ,'%d' %i] = fun(x[times],i)
    state_list.append(state)
        #print(result)
#omsriramajayam
df_state_list = pd.DataFrame(state_list)
df_state_list.to_excel('random_combination_of_one_and_zero_%d_combinations_all_zeros.xlsx' %number_of_combinations, header = None, index = False)
#df_state_list.to_excel('random_combination_of_one_and_zero_%d_combinations_different_fraction.xlsx' %number_of_combinations, header = None, index = False) #for first fraction list
list_of_rcs_over_frequency.to_excel("RCS_over_selected_frequencies_for_random_combinations_%d_combinations_all_zeros.xlsx" %number_of_combinations) 

for k in range(list_of_rcs_over_frequency.shape[0]):
    plt.figure()
    plt.xlabel("Frequency GHz")
    plt.ylabel("RCS reduction in dB")
    #plt.title("RCS reduction for %d combination of V1 and V2 from 6GHz to 14GHz \n" %k, loc = 'right')
    plt.title("RCS reduction for all V1 from 6GHz to 14GHz", loc = 'right')
    plt.plot(df_v1["frequency"][0:number_of_frequency_points],list_of_rcs_over_frequency.loc['%d' %k,:], label = "All zeros")#"%d combination" %k)
    plt.legend(loc = "upper right")
    #plt.savefig("RCS_over_selected_frequency_for_random_combination_number_different_fraction_%d_%%d.png" %k %number_of_frequency_points)
    plt.savefig("RCS_over_selected_frequency_for_all_zeros.png")
plt.show()
plt.ion() # helps to come to next line in command window without cosing figures
