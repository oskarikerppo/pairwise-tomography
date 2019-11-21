"""
Pairwise tomography circuit generation
"""
import copy
import numpy as np

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit.ignis.verification.tomography.basis.circuits import _format_registers

def pairwise_state_tomography_circuits(circuit, measured_qubits):
    """
    Generates a minimal set of circuits for pairwise state tomography.

    This performs measurement in the Pauli-basis resulting in 
    circuits for an n-qubit state tomography experiment.

    Args:
        circuit (QuantumCircuit): the state preparation circuit to be
                                  tomographed.
        measured_qubits (list): list of the indices of qubits to be measured
    Returns:
        A list of QuantumCircuit objects containing the original circuit
        with state tomography measurements appended at the end.
    """

    ### Initialisation stuff

    #TODO: measured_qubits should be like in the ignis tomography functions, 
    # i.e. it should be a QuantumRegister or a list of QuantumRegisters
    if isinstance(measured_qubits, list):
        # Unroll list of registers
        meas_qubits = _format_registers(*measured_qubits)
    else:
        meas_qubits = _format_registers(measured_qubits)
    
    print(meas_qubits)
    N = len(meas_qubits)
    
    cr = ClassicalRegister(len(meas_qubits))
    print(cr)
    qr = circuit.qregs[0]
    
    ### Uniform measurement settings
    X = copy.deepcopy(circuit)
    Y = copy.deepcopy(circuit)
    Z = copy.deepcopy(circuit)
    
    X.add_register(cr)
    Y.add_register(cr)
    Z.add_register(cr)
    
    X.name = str(('X',)*N)
    Y.name = str(('Y',)*N)
    Z.name = str(('Z',)*N)

    for bit_index, qubit in enumerate(meas_qubits):

        X.h(qubit)
        Y.sdg(qubit)
        Y.h(qubit)
        
        X.measure(qubit, cr[bit_index])
        Y.measure(qubit, cr[bit_index])
        Z.measure(qubit, cr[bit_index])
    
    output_circuit_list = [X, Y, Z]
    
    ### Heterogeneous measurement settings
    # Generation of six possible sequences
    sequences = []
    meas_bases = ['X', 'Y', 'Z']
    for i in range(3):
        for j in range(2):
            meas_bases_copy = meas_bases[:]
            sequence = [meas_bases_copy[i]]
            meas_bases_copy.remove(meas_bases_copy[i])
            sequence.append(meas_bases_copy[j])
            meas_bases_copy.remove(meas_bases_copy[j])
            sequence.append(meas_bases_copy[0])
            sequences.append(sequence)
    
    # Qubit colouring
    nlayers = int(np.ceil(np.log(float(N))/np.log(3.0)))
    pairs = {}

    for layout in range(nlayers):
        for sequence in sequences:
            meas_layout = copy.deepcopy(circuit)
            meas_layout.add_register(cr)
            meas_layout.name = ()
            for bit_index, qubit in enumerate(meas_qubits):
                local_basis = sequence[int(float(bit_index)/float(3**layout))%3]
                if local_basis == 'Y':
                    meas_layout.sdg(qubit)
                if local_basis != 'Z':
                    meas_layout.h(qubit)
                meas_layout.measure(qubit, cr[bit_index])
                meas_layout.name += (local_basis,)
            meas_layout.name = str(meas_layout.name)
            output_circuit_list.append(meas_layout)
    
    return output_circuit_list