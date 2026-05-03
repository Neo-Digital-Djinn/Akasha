from akasha_phase_engine.phase import (
    Phase, PhaseRegistry, PhaseTransition,
    SymmetryBreakingPattern, OrderParameter,
    ContinuousSymmetry, DiscreteSymmetry, SpaceTimeSymmetry, GaugeSymmetry,
    TopologicalProperties, TopologicalInvariant,
    QuantumProperties, QuantumCoherence, EntanglementStructure,
    DynamicalProperties, DrivenDynamics, TimeEvolution,
    ExperimentalCharacterization, ExperimentalTechnique, SpectroscopicSignature, TransportSignature,
    Material
)
import numpy as np


def build_default_registry() -> PhaseRegistry:
    registry = PhaseRegistry()

    # =========================================================================
    # CRYSTAL
    # =========================================================================
    registry.register(Phase(
        name="Crystal",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={SpaceTimeSymmetry.TRANSLATION, SpaceTimeSymmetry.ROTATION},
            broken_to={DiscreteSymmetry.D6},
            order_parameter=OrderParameter(
                name="Density wave",
                symbol="ρ(r)",
                physical_meaning="Periodic modulation of atomic density",
                units="atoms/cm³",
                symmetry_representation="scalar",
                field_theory="φ⁴ theory",
                critical_exponent_beta=0.326,
                universality_class="3D Ising",
                measurement_technique=["X-ray diffraction", "Neutron scattering", "Electron diffraction"]
            ),
            spontaneous=True,
            universality_class="3D Ising",
            num_goldstone_modes=3,
            goldstone_dispersion="ω ~ k² (acoustic phonons)",
            topological_defects=["Dislocations", "Grain boundaries", "Vacancies"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            berry_phase=0.0,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
                tensor_network_structure="MPS/PEPS"
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(
                ergodic=True,
                integrable=False,
            )
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Sharp Bragg peaks in X-ray diffraction",
                "Phonon dispersion with acoustic and optical branches",
                "Specific heat C ~ T³ at low T (Debye)",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="X-ray diffraction",
                    energy_range=(1000, 100000),
                    characteristic_features=["Bragg peaks at reciprocal lattice vectors G"]
                ),
                SpectroscopicSignature(
                    technique="Raman / Neutron scattering",
                    energy_range=(0, 200),
                    characteristic_features=["Acoustic phonons ω~k", "Optical phonon gap"]
                )
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="X-ray diffraction",
                    measures="Crystal structure, lattice constants",
                    typical_setup="Rotating anode or synchrotron source"
                )
            ]
        ),

        materials=[
            Material(
                formula="NaCl",
                crystal_structure="FCC (rock salt)",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 1074),
                lattice_constants=(5.64,),
                band_gap=8.5,
                synthesis_method=["Evaporation", "Melt growth"],
                commercially_available=True,
                cost_per_gram=0.01
            ),
            Material(
                formula="Si",
                crystal_structure="Diamond cubic",
                space_group="Fd-3m (No. 227)",
                temperature_range=(0, 1687),
                lattice_constants=(5.43,),
                band_gap=1.12,
                synthesis_method=["Czochralski", "Float zone"],
                commercially_available=True,
                cost_per_gram=0.05
            )
        ],
        prototype_material="NaCl",

        discovery_year=1912,
        discovered_by="von Laue (X-ray diffraction of crystals)",
        key_theoretical_papers=["Born & von Karman, Phys. Z. 13, 297 (1912)"],
        key_experimental_papers=["von Laue, Nobel Prize 1914"],
        textbook_references=["Ashcroft & Mermin, Solid State Physics (1976)"],

        technological_applications=[
            "Semiconductors (Si, Ge) — entire electronics industry",
            "Optical crystals (NaCl, LiNbO₃) — lasers, optics",
            "Piezoelectrics (quartz) — sensors, oscillators",
        ],
        open_questions=[
            "Prediction of crystal structure from composition alone",
            "Glass vs crystal: what determines which forms?",
        ]
    ))

    # =========================================================================
    # FERROMAGNET
    # =========================================================================
    registry.register(Phase(
        name="Ferromagnet",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={ContinuousSymmetry.SO3},
            broken_to={ContinuousSymmetry.SO2},
            order_parameter=OrderParameter(
                name="Magnetization",
                symbol="M",
                physical_meaning="Net magnetic moment per unit volume",
                units="A/m",
                symmetry_representation="vector",
                complex_valued=False,
                field_theory="Heisenberg model / φ⁴",
                critical_exponent_beta=0.365,
                correlation_length_exponent=0.705,
                universality_class="3D Heisenberg",
                measurement_technique=["Magnetometry", "Neutron scattering", "Magneto-optic Kerr"]
            ),
            spontaneous=True,
            explicit_breaking_term="h·M (applied field)",
            critical_temperature=1043.0,  # Fe Curie temperature, Kelvin
            universality_class="3D Heisenberg",
            num_goldstone_modes=2,
            goldstone_dispersion="ω ~ k² (magnons)",
            topological_defects=["Domain walls", "Skyrmions", "Vortices"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            berry_phase=np.pi,
            quantum_phase_transition=True,
            qpt_universality_class="3D Heisenberg",
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Spontaneous magnetization below T_C",
                "Hysteresis loop M(H)",
                "Magnon dispersion ω ~ k² (spin waves)",
                "Curie-Weiss susceptibility χ ~ 1/(T-T_C) above T_C",
            ],
            transport=TransportSignature(
                hall_coefficient="Anomalous Hall effect R_H ≠ 0 without B",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="SQUID magnetometry",
                    measures="Magnetization M(T,H)",
                    typical_setup="SQUID, 1.8-400K, 0-7T"
                ),
                ExperimentalTechnique(
                    name="Neutron scattering",
                    measures="Spin structure, magnon dispersion",
                    typical_setup="Triple-axis spectrometer"
                )
            ]
        ),

        materials=[
            Material(
                formula="Fe",
                crystal_structure="BCC",
                space_group="Im-3m (No. 229)",
                temperature_range=(0, 1043),
                synthesis_method=["Bulk growth", "Sputtering", "MBE"],
                commercially_available=True,
                cost_per_gram=0.001
            ),
            Material(
                formula="Ni",
                crystal_structure="FCC",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 627),
                synthesis_method=["Bulk growth", "Electrodeposition"],
                commercially_available=True,
                cost_per_gram=0.01
            )
        ],
        prototype_material="Fe (T_C = 1043 K)",

        discovery_year=1895,
        discovered_by="Pierre Curie (Curie law, 1895)",
        theoretical_prediction_year=1928,
        key_theoretical_papers=["Heisenberg, Z. Phys. 49, 619 (1928) - exchange interaction"],
        review_papers=["Coey, Magnetism and Magnetic Materials (2010)"],

        technological_applications=[
            "Magnetic storage (hard drives)",
            "Electric motors and generators",
            "Transformers",
            "Spintronics (GMR read heads)",
        ],
        open_questions=[
            "Quantitative ab initio prediction of T_C",
            "Skyrmion dynamics for racetrack memory",
            "Quantum spin liquids vs ordered magnets",
        ]
    ))

    # =========================================================================
    # TOPOLOGICAL INSULATOR (Bi₂Se₃)
    # =========================================================================
    registry.register(Phase(
        name="Topological Insulator",
        category="Topological",
        dimensionality=3,

        symmetry_breaking=None,  # TI breaks NO symmetry!

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Z₂",
            invariants_3d=[
                TopologicalInvariant(
                    name="Z₂ invariant",
                    symbol="ν",
                    value=1,
                    physical_meaning="Counts surface Dirac cones modulo 2",
                    cohomology_group="H²(BZ, Z₂)",
                    homotopy_group="Second Stiefel-Whitney class",
                    k_theory="KO theory, d=3, Class AII",
                    observable_consequence=[
                        "Odd number of surface Dirac cones",
                        "Protected by time-reversal symmetry",
                        "Surface states cannot be gapped without breaking T",
                        "π Berry phase around TRIM points"
                    ],
                    protected_by={SpaceTimeSymmetry.TIME_REVERSAL},
                    robust_to_disorder=True,
                    quantization="exact"
                )
            ],
            bulk_gap=True,
            edge_states=True,
            edge_state_dispersion="Linear Dirac: E = ℏv_F k, v_F ≈ 5×10⁵ m/s",
            ground_state_degeneracy=1,
            topological_entanglement_entropy=0.0,
            long_range_entanglement=False,
            anyonic_excitations=False,
            topological_field_theory="(3+1)D θ-term: θ=π in action"
        ),

        quantum=QuantumProperties(
            coherence=QuantumCoherence(
                coherence_length_zero_temp=float('inf'),
                decoherence_time=1e-12,
                decoherence_mechanism=[
                    "Phonon scattering (T > 10K)",
                    "Impurity scattering",
                    "Electron-electron scattering (surface)"
                ]
            ),
            entanglement=EntanglementStructure(
                area_law=True,
                long_range_entanglement=False,
                short_range_entanglement=True,
                entanglement_entropy_formula="S = α L² - γ + O(1/L)",
                tensor_network_structure="PEPS for 2D surface",
                bond_dimension=2
            ),
            berry_phase=np.pi,
            berry_curvature="Concentrated near band inversion points"
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Single Dirac cone at Γ̄ point (ARPES)",
                "Linear dispersion E = ℏv_F k",
                "Spin-momentum locking: ⟨S⟩ ∝ k×z",
                "Weak antilocalization in magnetotransport",
                "√B Landau level spacing (Dirac fermions)"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="ARPES",
                    energy_range=(-0.5, 0.5),
                    characteristic_features=[
                        "Dirac cone crossing E_F at Γ̄",
                        "No gap at Dirac point",
                        "Hexagonal warping at high E",
                        "Fermi velocity v_F ≈ 5×10⁵ m/s"
                    ]
                ),
                SpectroscopicSignature(
                    technique="STM/STS",
                    energy_range=(-0.3, 0.3),
                    characteristic_features=[
                        "Landau levels: E_n = ±√(2eℏv_F²Bn)",
                        "Zero mode at n=0",
                        "Berry phase π from LL fan diagram"
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="σ(T) = σ₀ + αT² (2D Dirac)",
                hall_coefficient="R_H = 1/(en_s) where n_s = surface density"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="ARPES with spin resolution",
                    measures="Band structure + spin texture",
                    resolution=10.0,
                    typical_setup="Synchrotron + Mott detector"
                ),
                ExperimentalTechnique(
                    name="Low-temperature magnetotransport",
                    measures="Weak antilocalization, SdH oscillations",
                    typical_setup="Dilution fridge (< 100 mK) + 14T magnet"
                )
            ],
            sample_purity_required="n < 10¹⁷ cm⁻³ bulk defects",
            temperature_control=(0.02, 300)
        ),

        materials=[
            Material(
                formula="Bi₂Se₃",
                crystal_structure="Rhombohedral",
                space_group="R-3m (No. 166)",
                temperature_range=(0, 300),
                lattice_constants=(4.138, 4.138, 28.636),
                band_gap=0.3,
                carrier_density=1e19,
                synthesis_method=["Bridgman", "MBE", "CVD", "Exfoliation"],
                commercially_available=True,
                cost_per_gram=10.0,
                discovery_paper="Hsieh et al., Nature 452, 970 (2008)",
                doi="10.1038/nature06843"
            ),
            Material(
                formula="Bi₂Te₃",
                crystal_structure="Rhombohedral",
                space_group="R-3m (No. 166)",
                temperature_range=(0, 300),
                synthesis_method=["Bridgman", "Zone melting"],
                commercially_available=True,
                cost_per_gram=15.0
            ),
            Material(
                formula="Sb₂Te₃",
                crystal_structure="Rhombohedral",
                space_group="R-3m (No. 166)",
                temperature_range=(0, 300),
                synthesis_method=["Bridgman"],
                commercially_available=True,
                cost_per_gram=12.0
            )
        ],
        prototype_material="Bi₂Se₃ (band gap 0.3 eV, most studied)",

        discovery_year=2007,
        theoretical_prediction_year=2007,
        experimental_confirmation_year=2008,
        discovered_by="Fu, Kane, Mele (theory) / Hsieh et al. (experiment)",
        key_theoretical_papers=[
            "Fu, Kane, Mele, PRL 98, 106803 (2007) - Z₂ classification",
            "Moore & Balents, PRB 75, 121306 (2007) - Strong TI",
            "Roy, PRB 79, 195322 (2009) - Material predictions"
        ],
        key_experimental_papers=[
            "Hsieh et al., Nature 452, 970 (2008) - First ARPES on Bi₂Se₃",
            "Chen et al., Science 325, 178 (2009) - Spin-resolved ARPES",
            "Xia et al., Nature Physics 5, 398 (2009) - Bi₂Te₃"
        ],
        review_papers=[
            "Hasan & Kane, RMP 82, 3045 (2010)",
            "Qi & Zhang, RMP 83, 1057 (2011)"
        ],
        textbook_references=[
            "Bernevig & Hughes, Topological Insulators (2013)",
            "Asbóth et al., A Short Course on TIs (2016)"
        ],

        technological_applications=[
            "Spintronics: spin-momentum locked currents",
            "Quantum computing: Majorana fermion platform (TI + superconductor)",
            "Thermoelectrics: Bi₂Te₃ ZT > 1 already commercial",
        ],
        potential_applications=[
            "Topological transistor (dissipationless)",
            "Terahertz detectors (Dirac plasmons)",
            "Magnetic memory (topological magnetoelectric effect)"
        ],
        open_questions=[
            "Can we achieve room-temperature topological transistor?",
            "How to completely suppress bulk conductivity?",
            "Many-body effects on surface Dirac fermions?",
            "Fractional topological insulator?",
            "Interplay with magnetism and superconductivity?",
        ],
        controversies=[
            "Bulk vs surface contribution to measured transport",
            "Whether Bi₂Se₃ thin films are truly 2D TI",
            "Role of hexagonal warping in topological protection"
        ]
    ))

    # =========================================================================
    # TIME CRYSTAL
    # =========================================================================
    registry.register(Phase(
        name="Time Crystal",
        category="Non-Equilibrium",
        dimensionality=1,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={SpaceTimeSymmetry.TIME_REVERSAL},
            broken_to={DiscreteSymmetry.Z2},
            order_parameter=OrderParameter(
                name="Subharmonic magnetization",
                symbol="M(2T)",
                physical_meaning="Spin polarization oscillating at half the drive frequency",
                units="dimensionless",
                symmetry_representation="scalar",
                field_theory="Floquet-MBL",
                measurement_technique=["NMR", "Spin echo", "Qubit readout"]
            ),
            spontaneous=True,
            universality_class="Floquet-MBL",
            num_goldstone_modes=0,
            topological_defects=[]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
        ),

        quantum=QuantumProperties(
            quantum_phase_transition=True,
            qpt_universality_class="Floquet-MBL",
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
                tensor_network_structure="MPS (MBL phase)"
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=False,
            far_from_equilibrium=True,
            driven=DrivenDynamics(
                floquet_system=True,
                drive_frequency=1e9,      # ~GHz typical
                prethermal_regime=True,
                prethermal_timescale=1e-3  # ms before heating
            ),
            time_evolution=TimeEvolution(
                ergodic=False,
                many_body_localized=True,
                integrable=False,
                chaotic=False
            )
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Spin echo at 2T (subharmonic response)",
                "Rigid period doubling robust to perturbations",
                "Persistence over many drive cycles (MBL protected)",
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="NMR / spin echo",
                    measures="Subharmonic magnetization oscillation",
                    typical_setup="Pulsed NMR, strong disorder"
                ),
                ExperimentalTechnique(
                    name="Trapped ion / superconducting qubit",
                    measures="Qubit state vs drive cycle",
                    typical_setup="Dilution fridge + microwave drive"
                )
            ]
        ),

        materials=[
                Material(
                formula="P-doped diamond (¹³C)",
                crystal_structure="Diamond cubic",
                space_group="Fd-3m (No. 227)",
                temperature_range=(0, 300),
                doping_required="Disordered P impurities ~10¹⁷ cm⁻³",
                synthesis_method=["CVD with isotopic control"],
                commercially_available=False,
                discovery_paper="Choi et al., Nature 543, 221 (2017)",
                doi="10.1038/nature21426"
            )
        ],
        prototype_material="Disordered ¹³C diamond (NV centers)",

        discovery_year=2016,
        theoretical_prediction_year=2012,
        experimental_confirmation_year=2017,
        discovered_by="Wilczek (theory, 2012) / Zhang et al., Choi et al. (experiment, 2017)",
        key_theoretical_papers=[
            "Wilczek, PRL 109, 160401 (2012) - Original proposal",
            "Khemani et al., PRL 116, 250401 (2016) - Floquet-MBL DTC",
            "Else et al., PRL 117, 090402 (2016) - Prethermal DTC"
        ],
        key_experimental_papers=[
            "Zhang et al., Nature 543, 217 (2017) - Trapped ions",
            "Choi et al., Nature 543, 221 (2017) - Diamond NV centers"
        ],
        review_papers=[
            "Sacha & Zakrzewski, Rep. Prog. Phys. 81, 016401 (2018)",
            "Zeng & Sheng, PRB 96, 094202 (2017)"
        ],

        technological_applications=[
            "Ultra-precise atomic clocks (time standard)",
            "Quantum memory (MBL-protected coherence)",
        ],
        potential_applications=[
            "Noise-resistant quantum computing",
            "Topological quantum sensors"
        ],
        open_questions=[
            "Can time crystals exist in equilibrium? (No — Watanabe-Oshikawa theorem)",
            "Thermodynamic limit: do they survive as N→∞?",
            "Non-equilibrium phases beyond MBL protection?",
            "Interplay with topological order?",
        ]
    ))

    # =========================================================================
    # BCS SUPERCONDUCTOR
    # =========================================================================
    registry.register(Phase(
        name="BCS Superconductor",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={GaugeSymmetry.U1_EM},
            broken_to=set(),
            order_parameter=OrderParameter(
                name="Cooper pair condensate",
                symbol="Δ",
                physical_meaning="Gap in quasiparticle spectrum; amplitude of Cooper pair wavefunction",
                units="meV",
                symmetry_representation="complex scalar",
                complex_valued=True,
                field_theory="BCS / Ginzburg-Landau",
                lagrangian="ℒ = |∂ψ|² - α|ψ|² + β|ψ|⁴",
                critical_exponent_beta=0.5,
                universality_class="Mean-field (BCS weak coupling)",
                measurement_technique=["Tunneling spectroscopy", "ARPES", "Specific heat jump"]
            ),
            spontaneous=True,
            critical_temperature=9.2,   # Nb T_c in Kelvin
            universality_class="Mean-field",
            num_goldstone_modes=0,      # Eaten by Higgs mechanism (Anderson-Higgs)
            topological_defects=["Abrikosov vortices (type-II)", "Domain walls"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=True,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            superposition=True,
            quantum_interference=True,
            tunneling=True,
            coherence=QuantumCoherence(
                coherence_length_zero_temp=39e-9,  # ~39 nm for Nb
                decoherence_mechanism=["Thermal fluctuations above T_c", "Magnetic impurities"],
            ),
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            ),
            berry_phase=0.0,
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Zero DC resistance below T_c",
                "Meissner effect: perfect diamagnetism (χ = -1)",
                "Energy gap Δ in tunneling spectrum",
                "Specific heat jump at T_c",
                "Flux quantization Φ₀ = h/2e"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Tunneling (STS/SIS)",
                    energy_range=(-10, 10),
                    characteristic_features=[
                        "Gap 2Δ in DOS",
                        "Coherence peaks at ±Δ",
                        "BCS ratio 2Δ/k_BT_c ≈ 3.52"
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="σ → ∞ (DC), σ(ω) has gap at ℏω < 2Δ",
                resistivity="ρ = 0 below T_c",
                hall_coefficient="R_H = 0 in Meissner state"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Four-probe resistance",
                    measures="T_c, zero resistance",
                    typical_setup="He-4 cryostat, 1.5-300K"
                ),
                ExperimentalTechnique(
                    name="SQUID magnetometry",
                    measures="Meissner effect, flux quantization",
                    typical_setup="SQUID + field-cooled/zero-field-cooled"
                )
            ],
            temperature_control=(0.01, 300)
        ),

        materials=[
            Material(
                formula="Nb",
                crystal_structure="BCC",
                space_group="Im-3m (No. 229)",
                temperature_range=(0, 9.2),
                band_gap=3.05e-3,  # 2Δ in eV
                synthesis_method=["Sputtering", "MBE", "Bulk crystal"],
                commercially_available=True,
                cost_per_gram=0.05
            ),
            Material(
                formula="Pb",
                crystal_structure="FCC",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 7.2),
                band_gap=2.73e-3,
                synthesis_method=["Thermal evaporation", "Bulk"],
                commercially_available=True,
                cost_per_gram=0.002
            ),
            Material(
                formula="YBa₂Cu₃O₇",
                crystal_structure="Orthorhombic (perovskite)",
                space_group="Pmmm (No. 47)",
                temperature_range=(0, 93),
                doping_required="Optimal oxygen doping (δ ≈ 0.07)",
                synthesis_method=["Solid-state reaction", "PLD", "Sputtering"],
                commercially_available=True,
                cost_per_gram=0.5,
                discovery_paper="Wu et al., PRL 58, 908 (1987)",
                doi="10.1103/PhysRevLett.58.908"
            )
        ],
        prototype_material="Nb (T_c = 9.2 K, workhorse of SC circuits)",

        neighboring_phases=["Normal Metal", "Topological Superconductor", "Ferromagnet"],

        discovery_year=1911,
        theoretical_prediction_year=1957,
        experimental_confirmation_year=1911,
        discovered_by="Onnes (experiment 1911) / Bardeen, Cooper, Schrieffer (theory 1957)",
        key_theoretical_papers=[
            "Bardeen, Cooper, Schrieffer, Phys. Rev. 108, 1175 (1957) - BCS theory",
            "Ginzburg & Landau, JETP 20, 1064 (1950) - GL theory",
            "Anderson, PRL 3, 325 (1958) - Higgs mechanism in SC"
        ],
        key_experimental_papers=[
            "Onnes, Leiden Comm. 120b (1911) - Discovery",
            "Josephson, Phys. Lett. 1, 251 (1962) - Josephson effect",
        ],
        review_papers=["Tinkham, Introduction to Superconductivity (2004)"],
        textbook_references=["de Gennes, Superconductivity of Metals and Alloys (1966)"],

        technological_applications=[
            "MRI machines (NbTi / Nb₃Sn magnets)",
            "Superconducting qubits (quantum computing)",
            "SQUID sensors (most sensitive magnetometers)",
            "Particle accelerator magnets (LHC)",
            "Maglev trains (Japan SCMaglev)",
        ],
        potential_applications=[
            "Room-temperature superconductor (holy grail)",
            "Lossless power transmission",
            "Topological quantum computing (SC + TI)"
        ],
        open_questions=[
            "Mechanism of high-T_c cuprate superconductivity",
            "Room-temperature superconductor: possible?",
            "Role of pseudogap in cuprates",
            "Interplay of SC and magnetism in unconventional SCs",
        ]
    ))

    # =========================================================================
    # FRACTIONAL QUANTUM HALL STATE (ν = 1/3)
    # =========================================================================
    registry.register(Phase(
        name="Fractional Quantum Hall State",
        category="Topological",
        dimensionality=2,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Abelian",
            invariants_2d=[
                TopologicalInvariant(
                    name="Chern number",
                    symbol="C",
                    value=1,
                    physical_meaning="Quantized Hall conductance σ_xy = νe²/h",
                    cohomology_group="H²(BZ, Z)",
                    k_theory="K-theory class",
                    observable_consequence=[
                        "Hall conductance σ_xy = (1/3)e²/h (ν=1/3 Laughlin)",
                        "Zero longitudinal conductance σ_xx = 0",
                        "Fractionally charged quasiparticles e* = e/3",
                        "Fractional (anyonic) braiding statistics"
                    ],
                    protected_by={SpaceTimeSymmetry.TIME_REVERSAL},
                    quantization="exact"
                )
            ],
            bulk_gap=True,
            edge_states=True,
            edge_state_dispersion="Chiral: E = ℏv_F k (unidirectional)",
            ground_state_degeneracy=3,               # ν=1/3 on torus: 3-fold
            ground_state_degeneracy_on_torus=3,
            ground_state_degeneracy_depends_on_genus=True,
            topological_entanglement_entropy=-0.549,  # γ = ln(√3)
            long_range_entanglement=True,
            anyonic_excitations=True,
            anyon_types=["e/3 Laughlin quasiparticle", "e/3 quasihole"],
            braiding_statistics="Abelian (θ = 2π/3)",
            topological_field_theory="U(1) Chern-Simons at level k=3"
        ),

        quantum=QuantumProperties(
            coherence=QuantumCoherence(
                decoherence_mechanism=["Disorder", "Inter-Landau-level mixing", "Phonons"]
            ),
            entanglement=EntanglementStructure(
                area_law=False,
                logarithmic_correction=True,
                long_range_entanglement=True,
                entanglement_entropy_formula="S = αL - γ, γ = ln(√3) ≈ 0.549",
            ),
            berry_phase=np.pi,
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Hall plateau σ_xy = (1/3)e²/h",
                "Zero longitudinal resistance ρ_xx → 0",
                "Fractional charge e/3 in shot noise",
                "Anyonic interference in Fabry-Perot geometry",
            ],
            transport=TransportSignature(
                conductivity="σ_xy = νe²/h (quantized), σ_xx = 0",
                hall_coefficient="R_xy = h/(νe²) = 3h/e²"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Low-temperature Hall transport",
                    measures="σ_xy, σ_xx vs B and T",
                    typical_setup="Dilution fridge < 30 mK, B > 10T"
                ),
                ExperimentalTechnique(
                    name="Shot noise",
                    measures="Fractional charge e/3",
                    typical_setup="High-frequency current noise measurement"
                )
            ],
            temperature_control=(0.01, 1.0)
        ),

        materials=[
            Material(
                formula="GaAs/AlGaAs",
                crystal_structure="Zincblende heterostructure",
                space_group="F-43m (No. 216)",
                temperature_range=(0, 1),
                doping_required="2DEG at interface, n ~ 10¹¹ cm⁻²",
                synthesis_method=["MBE (ultra-high purity)"],
                commercially_available=False,
                discovery_paper="Tsui, Störmer, Gossard, PRL 48, 1559 (1982)",
                doi="10.1103/PhysRevLett.48.1559"
            ),
            Material(
                formula="Graphene",
                crystal_structure="2D hexagonal",
                space_group="P6/mmm",
                temperature_range=(0, 20),
                doping_required="Ultra-clean, encapsulated in hBN",
                synthesis_method=["CVD", "Mechanical exfoliation"],
                commercially_available=True,
            )
        ],
        prototype_material="GaAs/AlGaAs 2DEG at ν=1/3",

        neighboring_phases=["Integer Quantum Hall State", "Wigner Crystal", "Normal Metal 2D"],

        discovery_year=1982,
        theoretical_prediction_year=1983,
        experimental_confirmation_year=1982,
        discovered_by="Tsui, Störmer, Gossard (experiment) / Laughlin (theory, 1983)",
        key_theoretical_papers=[
            "Laughlin, PRL 50, 1395 (1983) - Laughlin wavefunction",
            "Haldane, PRL 51, 605 (1983) - Hierarchy states",
            "Wen & Niu, PRB 41, 9377 (1990) - Topological order"
        ],
        key_experimental_papers=[
            "Tsui, Störmer, Gossard, PRL 48, 1559 (1982) - Discovery",
            "de-Picciotto et al., Nature 389, 162 (1997) - Fractional charge"
        ],
        review_papers=["Wen, Quantum Field Theory of Many-Body Systems (2004)"],
        textbook_references=["Yoshioka, The Quantum Hall Effect (2002)"],

        technological_applications=[
            "Resistance standard (quantum metrology)",
        ],
        potential_applications=[
            "Topological quantum computing (non-Abelian states at ν=5/2)",
            "Anyonic quantum gates"
        ],
        open_questions=[
            "Non-Abelian nature of ν=5/2 state (Moore-Read)?",
            "FQH in graphene and moiré systems",
            "Composite fermion Fermi sea at ν=1/2",
            "FQH without Landau levels (fractional Chern insulators)?",
        ]
    ))

    # =========================================================================
    # QUANTUM SPIN LIQUID
    # =========================================================================
    registry.register(Phase(
        name="Quantum Spin Liquid",
        category="Topological",
        dimensionality=2,

        symmetry_breaking=None,  # Breaks NO symmetry down to T=0!

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Z₂ (Z₂ QSL) or U(1) (U(1) QSL)",
            bulk_gap=False,   # Gapless spinons in U(1) QSL
            edge_states=False,
            ground_state_degeneracy=4,  # Z₂ QSL on torus
            ground_state_degeneracy_on_torus=4,
            topological_entanglement_entropy=-0.693,  # γ = ln(2) for Z₂
            long_range_entanglement=True,
            anyonic_excitations=True,
            anyon_types=["Spinon (charge-0, spin-1/2)", "Vison (Z₂ flux)", "Fermion (bound state)"],
            braiding_statistics="Abelian (Z₂)",
            topological_field_theory="Z₂ gauge theory / deconfined phase"
        ),

        quantum=QuantumProperties(
            quantum_fluctuations_suppress_order=True,
            entanglement=EntanglementStructure(
                area_law=False,
                logarithmic_correction=True,
                long_range_entanglement=True,
                entanglement_entropy_formula="S = αL - ln(2) + O(1/L)",
                tensor_network_structure="PEPS (approximate)"
            ),
            berry_phase=np.pi,
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(
                ergodic=False,
                integrable=False,
            )
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "No magnetic order down to T → 0",
                "Broad continuum in neutron scattering (spinon continuum)",
                "Linear T specific heat (spinons as Fermi surface)",
                "Wilson ratio W ≈ 1 (Fermi-liquid-like spinons)",
                "Absence of muon spin relaxation ordering"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Inelastic neutron scattering",
                    energy_range=(0, 50),
                    characteristic_features=[
                        "Broad spinon continuum (no sharp magnon)",
                        "Lower boundary ω ~ k (spinon dispersion)",
                        "No long-range order peaks"
                    ]
                )
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="μSR (muon spin rotation)",
                    measures="Local magnetic order / absence thereof",
                    typical_setup="ISIS / PSI muon facility"
                ),
                ExperimentalTechnique(
                    name="Inelastic neutron scattering",
                    measures="Spin excitation spectrum",
                    typical_setup="Spallation source + time-of-flight spectrometer"
                )
            ],
            temperature_control=(0.05, 20)
        ),

        materials=[
            Material(
                formula="α-RuCl₃",
                crystal_structure="Honeycomb layered",
                space_group="R-3 (No. 148)",
                temperature_range=(0, 300),
                doping_required="None; Kitaev interactions dominate",
                synthesis_method=["CVT (chemical vapor transport)", "Bridgman"],
                commercially_available=True,
                cost_per_gram=50.0,
                discovery_paper="Banerjee et al., Nature Materials 15, 733 (2016)"
            ),
            Material(
                formula="Herbertsmithite ZnCu₃(OH)₆Cl₂",
                crystal_structure="Kagome",
                space_group="R-3m (No. 166)",
                temperature_range=(0, 300),
                synthesis_method=["Hydrothermal synthesis"],
                commercially_available=False,
                discovery_paper="Shores et al., JACS 127, 13462 (2005)"
            )
        ],
        prototype_material="α-RuCl₃ (Kitaev QSL candidate)",

        neighboring_phases=["Ferromagnet", "Antiferromagnet", "Valence Bond Solid"],

        discovery_year=1973,
        theoretical_prediction_year=1973,
        experimental_confirmation_year=2016,
        discovered_by="Anderson (RVB theory 1973) / Banerjee et al. (α-RuCl₃, 2016)",
        key_theoretical_papers=[
            "Anderson, Materials Research Bulletin 8, 153 (1973) - RVB proposal",
            "Kitaev, Annals of Physics 321, 2 (2006) - Kitaev honeycomb model",
            "Wen, PRB 65, 165113 (2002) - Z₂ QSL and topological order"
        ],
        key_experimental_papers=[
            "Shores et al., JACS 127, 13462 (2005) - Herbertsmithite",
            "Banerjee et al., Nature Materials 15, 733 (2016) - Majorana evidence"
        ],
        review_papers=[
            "Savary & Balents, Rep. Prog. Phys. 80, 016502 (2017)",
            "Zhou et al., Rev. Mod. Phys. 89, 025003 (2017)"
        ],

        technological_applications=[],
        potential_applications=[
            "Topological quantum memory (Z₂ code)",
            "Fault-tolerant quantum computing (Kitaev model)",
            "Majorana-based quantum gates"
        ],
        open_questions=[
            "Does a true QSL exist in any real material?",
            "Smoking-gun experimental signature of topological order?",
            "Gapped vs gapless QSL: which is more common?",
            "Kitaev QSL in α-RuCl₃: confirmed or approximate?",
        ],
        controversies=[
            "Whether α-RuCl₃ is a true Kitaev QSL or proximate",
            "Herbertsmithite: QSL or valence bond glass?",
        ]
    ))

    # =========================================================================
    # WEYL SEMIMETAL
    # =========================================================================
    registry.register(Phase(
        name="Weyl Semimetal",
        category="Topological",
        dimensionality=3,

        symmetry_breaking=None,  # Requires broken T or P, but phase itself not SSB

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Chern (integer)",
            invariants_3d=[
                TopologicalInvariant(
                    name="Chern number (Weyl node)",
                    symbol="C",
                    value=1,
                    physical_meaning="Topological charge of each Weyl point; monopole of Berry curvature",
                    cohomology_group="H³(BZ, Z)",
                    homotopy_group="π₂(S²) = Z",
                    k_theory="K-theory Chern class",
                    observable_consequence=[
                        "Fermi arc surface states connecting Weyl nodes",
                        "Chiral anomaly: ∂_μ j^μ = E·B (non-conservation of chiral charge)",
                        "Negative longitudinal magnetoresistance",
                        "Anomalous Hall effect"
                    ],
                    protected_by={SpaceTimeSymmetry.TRANSLATION},
                    robust_to_disorder=False,
                    quantization="exact"
                )
            ],
            bulk_gap=False,   # Semimetal — gapless Weyl nodes
            edge_states=True,
            edge_state_dispersion="Fermi arcs: open arcs connecting ±C Weyl nodes",
            long_range_entanglement=False,
            anyonic_excitations=False,
        ),

        quantum=QuantumProperties(
            berry_phase=np.pi,
            berry_curvature="Monopole at each Weyl node: Ω_n(k) = C·k̂/|k|²",
            entanglement=EntanglementStructure(area_law=True)
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Fermi arc surface states (ARPES)",
                "Negative longitudinal magnetoresistance (chiral anomaly)",
                "Anomalous Hall effect without net magnetization",
                "Chiral magnetic effect (current ∝ B)",
                "Quantum oscillations from bulk Weyl pockets"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="ARPES",
                    energy_range=(-0.3, 0.3),
                    characteristic_features=[
                        "Fermi arcs connecting projected Weyl nodes",
                        "Non-closed Fermi surface (bulk Weyl cones)",
                        "Spin-momentum locking on arcs"
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="σ_xx increases with B when E∥B (negative MR)",
                hall_coefficient="Large anomalous Hall R_H even at B=0"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="ARPES",
                    measures="Fermi arc topology",
                    typical_setup="Synchrotron, <20K"
                ),
                ExperimentalTechnique(
                    name="Magnetotransport",
                    measures="Negative MR, anomalous Hall",
                    typical_setup="Dilution fridge + rotatable magnet"
                )
            ]
        ),

        materials=[
            Material(
                formula="TaAs",
                crystal_structure="Body-centered tetragonal (non-centrosymmetric)",
                space_group="I4₁md (No. 109)",
                temperature_range=(0, 300),
                synthesis_method=["CVT", "Flux growth"],
                commercially_available=True,
                cost_per_gram=20.0,
                discovery_paper="Lv et al., PRX 5, 031013 (2015)",
                doi="10.1103/PhysRevX.5.031013"
            ),
            Material(
                formula="NbAs",
                crystal_structure="Body-centered tetragonal",
                space_group="I4₁md (No. 109)",
                temperature_range=(0, 300),
                synthesis_method=["CVT"],
                commercially_available=False,
            )
        ],
        prototype_material="TaAs (first experimentally confirmed Weyl semimetal)",

        neighboring_phases=["Topological Insulator", "Normal Metal", "Dirac Semimetal"],

        discovery_year=2015,
        theoretical_prediction_year=2011,
        experimental_confirmation_year=2015,
        discovered_by="Wan et al. (theory 2011) / Lv et al., Xu et al. (experiment 2015)",
        key_theoretical_papers=[
            "Wan et al., PRB 83, 205101 (2011) - First prediction in pyrochlore iridates",
            "Burkov & Balents, PRL 107, 127205 (2011) - Weyl semimetal proposal",
            "Huang et al., Nature Comm. 6, 7373 (2015) - TaAs prediction"
        ],
        key_experimental_papers=[
            "Lv et al., PRX 5, 031013 (2015) - Fermi arcs in TaAs",
            "Xu et al., Science 349, 613 (2015) - Weyl nodes in TaAs"
        ],
        review_papers=[
            "Armitage, Mele, Vishwanath, RMP 90, 015001 (2018)",
        ],

        technological_applications=[
            "Spintronics: large anomalous Hall currents",
            "Topological electronics: chiral transport",
        ],
        potential_applications=[
            "Ultra-fast optical response (chiral anomaly)",
            "Quantum computing (Fermi arc transport)"
        ],
        open_questions=[
            "Can chiral anomaly be exploited for devices?",
            "Magnetic Weyl semimetals at room temperature?",
            "Weyl-superconductor interface: new topological phases?",
        ]
    ))

    # =========================================================================
    # MOTT INSULATOR
    # =========================================================================
    registry.register(Phase(
        name="Mott Insulator",
        category="Strongly-Correlated",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={ContinuousSymmetry.SO3, SpaceTimeSymmetry.TRANSLATION},
            broken_to={DiscreteSymmetry.Z2},
            order_parameter=OrderParameter(
                name="Staggered magnetization",
                symbol="m_s",
                physical_meaning="Alternating spin polarization on A/B sublattices",
                units="μ_B / unit cell",
                symmetry_representation="vector",
                field_theory="Heisenberg antiferromagnet",
                universality_class="3D Heisenberg",
                measurement_technique=["Neutron scattering", "μSR", "NMR"]
            ),
            spontaneous=True,
            universality_class="3D Heisenberg (AF)",
            num_goldstone_modes=2,
            goldstone_dispersion="ω ~ k (magnons, linear)",
            topological_defects=["Domain walls", "Vortices"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=True,   # Mott gap (Hubbard U)
        ),

        quantum=QuantumProperties(
            quantum_phase_transition=True,
            qpt_critical_point=None,   # Bandwidth-controlled MIT
            qpt_universality_class="Mott transition (first order typically)",
            quantum_fluctuations_suppress_order=True,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False, integrable=False)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Insulating behavior despite partially-filled band (band theory fails)",
                "Antiferromagnetic order in most Mott insulators",
                "Large optical gap > bandwidth prediction",
                "Doping → high-T_c superconductivity (cuprates)",
                "Hubbard bands in photoemission"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="ARPES / PES",
                    energy_range=(-10, 2),
                    characteristic_features=[
                        "Lower Hubbard band below E_F",
                        "Upper Hubbard band above E_F",
                        "Gap = Mott-Hubbard gap U-W",
                        "No coherent quasiparticle peak"
                    ]
                )
            ],
            transport=TransportSignature(
                resistivity="ρ(T) ~ exp(Δ/k_BT) (activated)",
                conductivity="σ → 0 as T → 0"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Optical spectroscopy",
                    measures="Mott gap, optical conductivity σ(ω)",
                    typical_setup="FTIR + UV-Vis, 10-300K"
                )
            ]
        ),

        materials=[
            Material(
                formula="La₂CuO₄",
                crystal_structure="K₂NiF₄ structure (layered perovskite)",
                space_group="Bmab (No. 64)",
                temperature_range=(0, 325),
                band_gap=2.0,   # Mott gap, eV
                synthesis_method=["Solid-state reaction", "Floating zone"],
                commercially_available=True,
                discovery_paper="Bednorz & Müller, Z. Phys. B 64, 189 (1986)"
            ),
            Material(
                formula="V₂O₃",
                crystal_structure="Corundum",
                space_group="R-3c (No. 167)",
                temperature_range=(0, 170),
                synthesis_method=["Arc melting", "CVT"],
                commercially_available=True,
                cost_per_gram=1.0
            )
        ],
        prototype_material="La₂CuO₄ (parent compound of cuprate superconductors)",

        neighboring_phases=["BCS Superconductor", "Normal Metal", "Quantum Spin Liquid"],

        discovery_year=1937,
        theoretical_prediction_year=1949,
        discovered_by="de Boer & Verwey (experiment 1937) / Mott (theory 1949)",
        key_theoretical_papers=[
            "Mott, Proc. Phys. Soc. A 62, 416 (1949) - Mott transition",
            "Hubbard, Proc. R. Soc. A 276, 238 (1963) - Hubbard model",
            "Georges et al., RMP 68, 13 (1996) - DMFT solution"
        ],
        key_experimental_papers=[
            "de Boer & Verwey, Proc. Phys. Soc. 49, 59 (1937) - Discovery",
            "Bednorz & Müller, Z. Phys. B 64, 189 (1986) - Cuprate SC from doped Mott"
        ],
        review_papers=["Imada, Fujimori, Tokura, RMP 70, 1039 (1998)"],

        technological_applications=[
            "Parent compound of cuprate high-T_c superconductors",
            "Neuromorphic computing (Mott memory, VO₂)",
            "Infrared sensors (VO₂ metal-insulator transition)"
        ],
        open_questions=[
            "Pseudogap in doped cuprates: Mott physics or other?",
            "Universal phase diagram of Mott transition?",
            "Orbital-selective Mott transition in multiband systems",
        ]
    ))

    # =========================================================================
    # BOSE-EINSTEIN CONDENSATE
    # =========================================================================
    registry.register(Phase(
        name="Bose-Einstein Condensate",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={ContinuousSymmetry.U1},
            broken_to=set(),
            order_parameter=OrderParameter(
                name="Macroscopic wavefunction",
                symbol="Ψ = √n₀ e^(iφ)",
                physical_meaning="Condensate fraction n₀ and global phase φ",
                units="m⁻³/²",
                symmetry_representation="complex scalar",
                complex_valued=True,
                field_theory="Gross-Pitaevskii / Bogoliubov",
                lagrangian="ℒ = iΨ*∂_tΨ - (ℏ²/2m)|∇Ψ|² - (g/2)|Ψ|⁴",
                critical_exponent_beta=0.349,
                universality_class="3D XY model",
                measurement_technique=["Absorption imaging", "Time-of-flight", "Interference"]
            ),
            spontaneous=True,
            universality_class="3D XY",
            num_goldstone_modes=1,
            goldstone_dispersion="ω ~ k (Bogoliubov phonons at low k)",
            topological_defects=["Quantized vortices (h/m circulation)", "Solitons"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,   # Gapless Goldstone (phonon) mode
            edge_states=False,
        ),

        quantum=QuantumProperties(
            superposition=True,
            quantum_interference=True,
            tunneling=True,
            coherence=QuantumCoherence(
                coherence_length_zero_temp=float('inf'),  # Long-range order
                decoherence_mechanism=["Three-body losses", "Thermal fluctuations", "Trap inhomogeneity"]
            ),
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
                tensor_network_structure="MPS (1D) / product state at mean field"
            ),
            berry_phase=0.0,
            quantum_phase_transition=True,
            qpt_universality_class="3D XY (BEC-Mott insulator QPT)"
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False, integrable=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Bimodal density profile: condensate peak + thermal cloud",
                "Long-range phase coherence (interference fringes)",
                "Quantized vortices in rotating BEC",
                "Bogoliubov phonon spectrum ω = ck at low k",
                "Sudden onset of condensate fraction at T_c"
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Bragg spectroscopy",
                    energy_range=(0, 1e-6),  # nK to μK scale
                    characteristic_features=[
                        "Linear phonon branch at low k",
                        "Free-particle dispersion at high k",
                        "Roton minimum (He-4 only)"
                    ]
                )
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="Absorption imaging (TOF)",
                    measures="Momentum distribution, condensate fraction",
                    typical_setup="Ultra-high vacuum + laser cooling + evaporative cooling"
                ),
                ExperimentalTechnique(
                    name="Interferometry",
                    measures="Phase coherence, vortex detection",
                    typical_setup="Two-path atom interferometer"
                )
            ],
            temperature_control=(1e-9, 1e-6)  # nK range
        ),

        materials=[
            Material(
                formula="⁸⁷Rb",
                crystal_structure="BEC (no crystal structure)",
                space_group="N/A",
                temperature_range=(0, 200e-9),  # < 200 nK
                synthesis_method=["Laser cooling + evaporative cooling in magnetic trap"],
                commercially_available=False,
                discovery_paper="Anderson et al., Science 269, 198 (1995)",
                doi="10.1126/science.269.5221.198"
            ),
            Material(
                formula="²³Na",
                crystal_structure="BEC",
                space_group="N/A",
                temperature_range=(0, 500e-9),
                synthesis_method=["Laser cooling + evaporative cooling"],
                commercially_available=False,
                discovery_paper="Davis et al., PRL 75, 3969 (1995)"
            ),
            Material(
                formula="⁴He",
                crystal_structure="Superfluid liquid",
                space_group="N/A",
                temperature_range=(0, 2.17),  # λ-point at 2.17K
                synthesis_method=["Cooling liquid helium below λ-point"],
                commercially_available=True,
                cost_per_gram=0.001
            )
        ],
        prototype_material="⁸⁷Rb (first atomic BEC, Anderson et al. 1995)",

        neighboring_phases=["Normal Bose Gas", "Superfluid He-4", "Mott Insulator (lattice BEC)"],

        discovery_year=1995,
        theoretical_prediction_year=1924,
        experimental_confirmation_year=1995,
        discovered_by="Bose & Einstein (theory 1924-25) / Cornell, Wieman, Ketterle (experiment 1995)",
        key_theoretical_papers=[
            "Bose, Z. Phys. 26, 178 (1924) - Bose statistics",
            "Einstein, Preuss. Akad. Wiss. (1925) - BEC prediction",
            "Bogoliubov, J. Phys. USSR 11, 23 (1947) - Excitation spectrum"
        ],
        key_experimental_papers=[
            "Anderson et al., Science 269, 198 (1995) - ⁸⁷Rb BEC",
            "Davis et al., PRL 75, 3969 (1995) - ²³Na BEC",
            "Bradley et al., PRL 75, 1687 (1995) - ⁷Li BEC"
        ],
        review_papers=[
            "Dalfovo et al., RMP 71, 463 (1999)",
            "Leggett, RMP 73, 307 (2001)"
        ],
        textbook_references=["Pitaevskii & Stringari, Bose-Einstein Condensation (2003)"],

        technological_applications=[
            "Atom interferometry (gravimeters, gyroscopes)",
            "Atomic clocks (optical lattice clocks)",
            "Quantum simulation of condensed matter models",
        ],
        potential_applications=[
            "Quantum computing with neutral atoms",
            "Precision tests of fundamental physics",
            "Atom lasers for lithography"
        ],
        open_questions=[
            "BEC of photons and exciton-polaritons: true condensate?",
            "BEC in neutron stars (pion/kaon condensation)?",
            "Strongly-correlated BEC beyond Bogoliubov theory",
        ]
    ))


    # =========================================================================
    # PARAMAGNET (ghost phase — transition endpoint, now full entry)
    # =========================================================================
    registry.register(Phase(
        name="Paramagnet",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            berry_phase=0.0,
            quantum_phase_transition=True,
            qpt_universality_class="3D Heisenberg",
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Linear M(H) susceptibility χ = C/T (Curie law)",
                "No hysteresis",
                "Spins fluctuate independently",
            ],
            transport=TransportSignature(
                hall_coefficient="Ordinary Hall effect only",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="SQUID magnetometry",
                    measures="Magnetisation vs T and H",
                    typical_setup="Vibrating sample magnetometer, 2-400 K"
                )
            ],
            temperature_control=(0.1, 1500)
        ),

        materials=[
            Material(
                formula="Fe (T > 1043 K)",
                crystal_structure="BCC",
                space_group="Im-3m (No. 229)",
                temperature_range=(1043, 1811),
                synthesis_method=["Elemental iron above Curie temperature"],
                commercially_available=True,
                cost_per_gram=0.001
            ),
        ],
        prototype_material="Fe above T_C = 1043 K",
        neighboring_phases=["Ferromagnet"],
        discovery_year=1895,
        discovered_by="Pierre Curie",
        key_theoretical_papers=["Curie, Ann. Chim. Phys. 5, 289 (1895)"],
        textbook_references=["Ashcroft & Mermin, Chapter 33"],
        open_questions=["Quantum critical fluctuations above quantum critical point"],
    ))

    # =========================================================================
    # NORMAL METAL (ghost phase — transition endpoint, now full entry)
    # =========================================================================
    registry.register(Phase(
        name="Normal Metal",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            berry_phase=0.0,
            entanglement=EntanglementStructure(
                area_law=False,
                volume_law=False,
                logarithmic_correction=True,
                entanglement_entropy_formula="S ~ L^(d-1) log L  (Fermi surface contribution)",
                tensor_network_structure=None,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Resistivity ρ ~ T² at low T (Fermi liquid)",
                "Linear specific heat C ~ γT (Sommerfeld)",
                "Pauli paramagnetism χ = const",
                "Finite resistivity at all T > 0",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="ARPES",
                    energy_range=(-3.0, 0.5),
                    characteristic_features=["Sharp quasiparticle peak at E_F", "Fermi surface"]
                )
            ],
            transport=TransportSignature(
                conductivity="σ ~ 1/T at high T; Fermi liquid σ ~ 1/T² at low T",
                resistivity="ρ ~ T² (Fermi liquid), ρ ~ T (strange metal)",
                hall_coefficient="R_H = -1/(ne)",
                thermal_conductivity="κ/T = const (Wiedemann-Franz)"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="4-probe resistivity",
                    measures="Electrical resistivity vs T",
                    typical_setup="Lock-in amplifier, He cryostat"
                )
            ],
            temperature_control=(0.01, 2000)
        ),

        materials=[
            Material(
                formula="Cu",
                crystal_structure="FCC",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 1358),
                lattice_constants=(3.615,),
                carrier_density=8.5e22,
                synthesis_method=["Smelting", "Electrodeposition"],
                commercially_available=True,
                cost_per_gram=0.009
            ),
            Material(
                formula="Au",
                crystal_structure="FCC",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 1337),
                lattice_constants=(4.078,),
                synthesis_method=["Smelting"],
                commercially_available=True,
                cost_per_gram=60.0
            ),
        ],
        prototype_material="Cu",
        neighboring_phases=["BCS Superconductor", "Mott Insulator"],
        discovery_year=1900,
        discovered_by="Drude (free electron model)",
        key_theoretical_papers=[
            "Drude, Ann. Phys. 1, 566 (1900)",
            "Sommerfeld, Z. Phys. 47, 1 (1928)"
        ],
        textbook_references=["Ashcroft & Mermin, Chapters 1-2"],
        open_questions=["Strange metal / non-Fermi liquid behaviour in cuprates"],
    ))

    # =========================================================================
    # NORMAL LIQUID (ghost phase — transition endpoint, now full entry)
    # =========================================================================
    registry.register(Phase(
        name="Normal Liquid",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=None,

        topology=TopologicalProperties(has_topological_order=False),

        quantum=QuantumProperties(
            berry_phase=0.0,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True, chaotic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "No long-range structural order (no Bragg peaks)",
                "Finite shear viscosity",
                "Diffusion of particles (D = k_B T / 6πηr)",
                "Structure factor S(q) with broad liquid peak",
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="X-ray / neutron liquid scattering",
                    measures="Pair distribution function g(r)",
                    typical_setup="Synchrotron or spallation source"
                )
            ],
            temperature_control=(200, 5000)
        ),

        materials=[
            Material(
                formula="H₂O",
                crystal_structure="Amorphous liquid",
                space_group="N/A",
                temperature_range=(273, 373),
                synthesis_method=["Melting ice"],
                commercially_available=True,
                cost_per_gram=0.0001
            ),
            Material(
                formula="Si (liquid)",
                crystal_structure="Metallic liquid",
                space_group="N/A",
                temperature_range=(1687, 3538),
                synthesis_method=["Melting silicon"],
                commercially_available=True,
                cost_per_gram=0.10
            ),
        ],
        prototype_material="H₂O",
        neighboring_phases=["Crystal", "Normal Bose Gas"],
        discovery_year=1687,
        discovered_by="Newton (Principia, viscosity of fluids)",
        key_theoretical_papers=[
            "van der Waals, Over de continuïteit (1873)",
            "Ornstein & Zernike, Proc. Akad. Sci. 17, 793 (1914)",
        ],
        textbook_references=["Hansen & McDonald, Theory of Simple Liquids (2006)"],
        open_questions=["Glass transition: liquid vs glass — is there a sharp transition?"],
    ))

    # =========================================================================
    # NORMAL BOSE GAS (ghost phase — transition endpoint, now full entry)
    # =========================================================================
    registry.register(Phase(
        name="Normal Bose Gas",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=None,

        topology=TopologicalProperties(has_topological_order=False),

        quantum=QuantumProperties(
            berry_phase=0.0,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Thermal (Bose-Einstein) momentum distribution",
                "No condensate peak in TOF imaging",
                "Bunching in Hanbury Brown-Twiss experiment",
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="Time-of-flight absorption imaging",
                    measures="Momentum distribution",
                    typical_setup="Ultra-high vacuum, laser cooling"
                )
            ],
            temperature_control=(100e-9, 10e-6)
        ),

        materials=[
            Material(
                formula="⁸⁷Rb (T > T_c)",
                crystal_structure="Dilute atomic gas",
                space_group="N/A",
                temperature_range=(170e-9, 1e-3),
                synthesis_method=["Laser cooling + partial evaporation"],
                commercially_available=False,
            ),
        ],
        prototype_material="⁸⁷Rb above BEC critical temperature ~170 nK",
        neighboring_phases=["Bose-Einstein Condensate"],
        discovery_year=1924,
        discovered_by="Bose & Einstein",
        key_theoretical_papers=["Bose, Z. Phys. 26, 178 (1924)"],
        textbook_references=["Pathria & Beale, Statistical Mechanics (2011)"],
        open_questions=["Strongly-interacting Bose gas beyond dilute limit"],
    ))

    # =========================================================================
    # TOPOLOGICAL SUPERCONDUCTOR (Kitaev chain / class D)
    # =========================================================================
    registry.register(Phase(
        name="Topological Superconductor",
        category="Topological",
        dimensionality=1,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={GaugeSymmetry.U1_SC},
            broken_to={DiscreteSymmetry.Z2},
            order_parameter=OrderParameter(
                name="p-wave pairing gap",
                symbol="Δ_p",
                physical_meaning="Odd-parity Cooper pair amplitude; topological when |μ| < 2|t|",
                units="meV",
                symmetry_representation="scalar",
                complex_valued=True,
                field_theory="Bogoliubov–de Gennes (BdG)",
                measurement_technique=["Tunneling spectroscopy", "NS junction conductance"]
            ),
            spontaneous=True,
            universality_class="Class D (BdG, no TRS, no spin rotation)",
            num_goldstone_modes=0,
            topological_defects=["Majorana zero modes at ends"]
        ),

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Z₂",
            invariants_1d=[
                TopologicalInvariant(
                    name="Kitaev Z₂ invariant",
                    symbol="ν",
                    value=1,
                    physical_meaning="Parity of occupied bands; ν=1 → Majorana end modes",
                    homotopy_group="π₀(C) = Z₂",
                    k_theory="KO⁻² (class D in d=1) = Z₂",
                    observable_consequence=[
                        "Zero-energy conductance peak e²/h in NS junction",
                        "4π-periodic Josephson effect",
                        "Non-Abelian braiding statistics of Majorana modes",
                    ],
                    protected_by={"particle-hole symmetry C"},
                    robust_to_disorder=True,
                    quantization="exact"
                )
            ],
            bulk_gap=True,
            edge_states=True,
            edge_state_dispersion="Zero-energy Majorana bound states (flat band at E=0)",
            ground_state_degeneracy=2,
            anyonic_excitations=True,
            anyon_types=["Majorana zero mode (non-Abelian Ising anyon)"],
            braiding_statistics="Non-Abelian",
            topological_field_theory="Z₂ gauge theory / Ising TQFT",
            long_range_entanglement=False,
        ),

        quantum=QuantumProperties(
            superposition=True,
            tunneling=True,
            quantum_phase_transition=True,
            qpt_critical_point=2.0,
            qpt_universality_class="Ising universality class (μ = ±2t critical points)",
            berry_phase=np.pi,
            berry_curvature="Concentrated at k=0 and k=π in topological phase",
            coherence=QuantumCoherence(
                decoherence_time=1e-6,
                decoherence_mechanism=[
                    "Quasiparticle poisoning",
                    "Charge noise",
                    "Phonon coupling",
                ]
            ),
            entanglement=EntanglementStructure(
                area_law=True,
                long_range_entanglement=False,
                short_range_entanglement=False,
                entanglement_entropy_formula="S = log 2  (ground state degeneracy correction)",
                tensor_network_structure="MPS with bond dimension 2"
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False, integrable=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Zero-bias conductance peak (ZBCP) of height e²/h in NS junction",
                "4π-periodic Josephson current (fractional Josephson effect)",
                "Quantised thermal conductance κ/T = (1/2)(π²k_B²/3h)",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Tunneling spectroscopy (NS junction)",
                    energy_range=(-1.0, 1.0),
                    characteristic_features=[
                        "Zero-bias peak pinned at E=0",
                        "Gap closing at topological phase transition",
                        "Induced gap Δ_ind in semiconductor"
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="2e²/h in topological phase (NS junction)",
                hall_coefficient="N/A (1D system)"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Dilution refrigerator + NS junction",
                    measures="Differential conductance dI/dV vs V",
                    typical_setup="InAs/Al or InSb/NbTiN nanowire, T < 50 mK, B ~ 0.5 T"
                ),
                ExperimentalTechnique(
                    name="Josephson junction spectroscopy",
                    measures="4π Josephson component",
                    typical_setup="RF-SQUID or microwave cavity"
                )
            ],
            sample_purity_required="Disorder must be weaker than topological gap",
            temperature_control=(0.01, 1.0)
        ),

        materials=[
            Material(
                formula="InAs/Al",
                crystal_structure="Zinc-blende nanowire + Al shell",
                space_group="F-43m (No. 216)",
                temperature_range=(0, 1.0),
                doping_required="n-type, gate-tunable to μ within topological window",
                band_gap=0.36,
                synthesis_method=["MBE nanowire growth", "In-situ Al deposition"],
                commercially_available=False,
                cost_per_gram=None,
                discovery_paper="Mourik et al., Science 336, 1003 (2012)",
                doi="10.1126/science.1222360"
            ),
            Material(
                formula="InSb/NbTiN",
                crystal_structure="Zinc-blende nanowire",
                space_group="F-43m (No. 216)",
                temperature_range=(0, 0.8),
                band_gap=0.17,
                synthesis_method=["MBE", "Sputtered NbTiN contact"],
                commercially_available=False,
                discovery_paper="Das et al., Nature Physics 8, 887 (2012)"
            ),
            Material(
                formula="Fe/Pb(110)",
                crystal_structure="Fe atomic chain on Pb surface",
                space_group="N/A",
                temperature_range=(0, 1.4),
                synthesis_method=["STM atom manipulation", "Self-assembly"],
                commercially_available=False,
                discovery_paper="Nadj-Perge et al., Science 346, 602 (2014)"
            ),
        ],
        prototype_material="InAs nanowire with epitaxial Al shell",

        neighboring_phases=["BCS Superconductor", "Normal Metal"],
        discovery_year=2012,
        theoretical_prediction_year=2001,
        experimental_confirmation_year=2012,
        discovered_by="Kitaev (theory 2001) / Mourik et al. (experiment 2012)",

        key_theoretical_papers=[
            "Kitaev, Physics-Uspekhi 44, 131 (2001) — Kitaev chain model",
            "Lutchyn et al., PRL 105, 077001 (2010) — semiconductor proposal",
            "Oreg et al., PRL 105, 177002 (2010) — nanowire proposal",
        ],
        key_experimental_papers=[
            "Mourik et al., Science 336, 1003 (2012) — first ZBCP",
            "Nadj-Perge et al., Science 346, 602 (2014) — Fe chains",
            "Microsoft (2023) — retractions and ongoing controversy",
        ],
        review_papers=[
            "Alicea, Rep. Prog. Phys. 75, 076501 (2012)",
            "Beenakker, Annu. Rev. Con. Mat. Phys. 4, 113 (2013)",
        ],
        textbook_references=["Bernevig & Hughes, Topological Insulators and Superconductors (2013)"],

        technological_applications=[
            "Topological quantum computing (Majorana qubits)",
            "Fault-tolerant quantum gates via non-Abelian braiding",
        ],
        potential_applications=[
            "Scalable topological quantum processor",
            "Decoherence-protected quantum memory",
        ],
        open_questions=[
            "Are observed ZBCPs truly topological Majoranas or trivial Andreev bound states?",
            "Can topological gap be made large enough for room-temperature operation?",
            "How to braid Majoranas without disturbing the quantum state?",
        ],
        controversies=[
            "2021-2023: Multiple high-profile Majorana papers retracted (Kouwenhoven group)",
            "Difficulty distinguishing topological from trivial ZBCPs experimentally",
        ]
    ))

    # =========================================================================
    # INTEGER QUANTUM HALL STATE (IQHE)
    # =========================================================================
    registry.register(Phase(
        name="Integer Quantum Hall State",
        category="Topological",
        dimensionality=2,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Integer (Chern)",
            invariants_2d=[
                TopologicalInvariant(
                    name="Chern number (TKNN invariant)",
                    symbol="C",
                    value=1,
                    physical_meaning="Number of filled Landau levels; Hall conductance = Ce²/h",
                    cohomology_group="H²(BZ, Z) = Z",
                    homotopy_group="π₁(U(N)) = Z",
                    k_theory="K⁰(T²) = Z",
                    observable_consequence=[
                        "Hall conductance σ_xy = Ce²/h (quantised to 1 part in 10⁹)",
                        "Chiral edge states: C branches crossing E_F",
                        "Zero longitudinal conductance σ_xx = 0 in plateau",
                    ],
                    protected_by={"magnetic field (no TRS)"},
                    robust_to_disorder=True,
                    quantization="exact"
                )
            ],
            bulk_gap=True,
            edge_states=True,
            edge_state_dispersion="Chiral edge mode: E ~ v_d · k (unidirectional)",
            ground_state_degeneracy=1,
            anyonic_excitations=False,
            topological_field_theory="U(1) Chern-Simons at level k",
            topological_entanglement_entropy=0.0,
            long_range_entanglement=False,
        ),

        quantum=QuantumProperties(
            superposition=True,
            quantum_interference=True,
            berry_phase=2 * np.pi,
            berry_curvature="Ω_n(k) = −2 Im ∑_{m≠n} <n|∂H/∂kx|m><m|∂H/∂ky|n> / (E_m−E_n)²",
            entanglement=EntanglementStructure(
                area_law=True,
                long_range_entanglement=False,
                entanglement_entropy_formula="S ~ L  (chiral edge contribution)",
                tensor_network_structure="PEPS"
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Hall resistance R_xy = h/(Ce²) quantised to 1 ppm",
                "Longitudinal resistance R_xx → 0 in plateau",
                "Plateaux in R_xy as function of B",
                "Chiral edge current immune to backscattering",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Transport (Hall bar geometry)",
                    energy_range=(0, 0.01),
                    characteristic_features=[
                        "Flat plateaux in σ_xy",
                        "Vanishing σ_xx at plateau centre",
                        "Landau level fan diagram in B-field",
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="σ_xy = Ce²/h (quantised), σ_xx = 0",
                hall_coefficient="R_H = h/(Ce²) — universal constant",
                thermal_conductivity="κ_xy = C(π²k_B²T/3h) (quantised)"
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Hall bar magnetotransport",
                    measures="R_xx and R_xy vs B and T",
                    typical_setup="2DEG (GaAs/AlGaAs or Si-MOSFET), T < 4K, B = 1–20 T"
                )
            ],
            sample_purity_required="High mobility μ > 10⁵ cm²/Vs for clean plateaux",
            temperature_control=(0.1, 4.0)
        ),

        materials=[
            Material(
                formula="GaAs/AlGaAs",
                crystal_structure="Zincblende heterostructure (2DEG)",
                space_group="F-43m (No. 216)",
                temperature_range=(0, 4.2),
                carrier_density=2e11,
                band_gap=1.42,
                synthesis_method=["MBE"],
                commercially_available=False,
                cost_per_gram=None,
                discovery_paper="von Klitzing et al., PRL 45, 494 (1980)"
            ),
            Material(
                formula="Si-MOSFET",
                crystal_structure="Si inversion layer (2DEG)",
                space_group="Fd-3m (No. 227)",
                temperature_range=(0, 4.2),
                synthesis_method=["Standard CMOS fabrication"],
                commercially_available=True,
            ),
            Material(
                formula="graphene/hBN",
                crystal_structure="Honeycomb monolayer",
                space_group="P6/mmm (No. 191)",
                temperature_range=(0, 300),
                band_gap=0.0,
                synthesis_method=["Mechanical exfoliation", "CVD"],
                commercially_available=False,
                discovery_paper="Novoselov et al., Nature 438, 197 (2005)"
            ),
        ],
        prototype_material="GaAs/AlGaAs 2DEG",

        neighboring_phases=["Fractional Quantum Hall State", "Normal Metal"],
        discovery_year=1980,
        theoretical_prediction_year=1982,
        experimental_confirmation_year=1980,
        discovered_by="von Klitzing (Nobel Prize 1985)",

        key_theoretical_papers=[
            "Thouless, Kohmoto, Nightingale, den Nijs (TKNN), PRL 49, 405 (1982)",
            "Laughlin, PRB 23, 5632 (1981) — gauge argument",
            "Halperin, PRB 25, 2185 (1982) — edge states",
        ],
        key_experimental_papers=[
            "von Klitzing, Dorda, Pepper, PRL 45, 494 (1980) — discovery",
        ],
        review_papers=[
            "Hasan & Kane, RMP 82, 3045 (2010)",
            "Ando, Matsumoto, Uemura, J. Phys. Soc. Jpn 39, 279 (1975)",
        ],
        textbook_references=[
            "Yoshioka, The Quantum Hall Effect (2002)",
            "Girvin, The Quantum Hall Effect: Novel Excitations and Broken Symmetries (1999)",
        ],

        technological_applications=[
            "Resistance standard (von Klitzing constant R_K = h/e² = 25812.807 Ω)",
            "Precision metrology — links resistance to fundamental constants",
        ],
        potential_applications=[
            "Chiral edge state interconnects (dissipationless)",
            "Topological quantum computation (with FQHE)",
        ],
        open_questions=[
            "Plateau-to-plateau transition: exact universality class?",
            "QHE in graphene without Landau levels (anomalous QHE)?",
        ],
    ))

    # =========================================================================
    # DIRAC SEMIMETAL
    # =========================================================================
    registry.register(Phase(
        name="Dirac Semimetal",
        category="Topological",
        dimensionality=3,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Z₂ (protected by crystal symmetry)",
            invariants_3d=[
                TopologicalInvariant(
                    name="Crystal symmetry protection",
                    symbol="C_n",
                    value=0,
                    physical_meaning="Dirac point is a Weyl node pair superposition; protected by rotation symmetry C_4 or C_6",
                    k_theory="Z (winding of Berry phase around Dirac point)",
                    observable_consequence=[
                        "Linear bulk band crossing at Dirac points",
                        "Fermi arc surface states connecting Dirac projections",
                        "3D Dirac cone: E = ±v_F |k|",
                    ],
                    protected_by={"time-reversal T", "inversion P", "crystal rotation C_n"},
                    robust_to_disorder=False,
                    quantization="approximate"
                )
            ],
            bulk_gap=False,
            edge_states=True,
            edge_state_dispersion="Fermi arcs on surface (shorter than Weyl semimetal arcs)",
            anyonic_excitations=False,
            topological_field_theory="Relativistic Dirac fermion in 3+1D",
            long_range_entanglement=False,
        ),

        quantum=QuantumProperties(
            berry_phase=np.pi,
            berry_curvature="Berry curvature dipole at each Dirac point",
            entanglement=EntanglementStructure(
                area_law=True,
                logarithmic_correction=True,
                entanglement_entropy_formula="S ~ L² log L  (Fermi point contribution)",
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "3D Dirac cone in ARPES: linear E(k) in all directions",
                "Linear magnetoresistance",
                "Fermi arc surface states",
                "Large non-saturating magnetoresistance",
                "Quantum oscillations with non-trivial Berry phase π",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="ARPES",
                    energy_range=(-1.0, 0.5),
                    characteristic_features=[
                        "Fourfold degenerate Dirac point at high-symmetry k",
                        "Linear dispersion in all momenta",
                        "Fermi arc surface states",
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="σ ~ T² at low T",
                hall_coefficient="Non-linear Hall with B",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="ARPES",
                    measures="3D band structure, Dirac cone, Fermi arcs",
                    typical_setup="Synchrotron + angle-resolved hemispherical analyser, T < 30 K"
                ),
                ExperimentalTechnique(
                    name="Quantum oscillations (SdH/dHvA)",
                    measures="Berry phase from oscillation phase",
                    typical_setup="High B (up to 60 T), T < 4 K, dilution refrigerator"
                )
            ],
            sample_purity_required="RRR > 1000 for clear quantum oscillations",
            temperature_control=(0.1, 100)
        ),

        materials=[
            Material(
                formula="Na₃Bi",
                crystal_structure="Hexagonal",
                space_group="P6₃/mmc (No. 194)",
                temperature_range=(0, 320),
                band_gap=0.0,
                lattice_constants=(5.448, 9.655),
                synthesis_method=["Flux growth", "Chemical vapour transport"],
                commercially_available=False,
                discovery_paper="Liu et al., Science 343, 864 (2014)",
                doi="10.1126/science.1245085"
            ),
            Material(
                formula="Cd₃As₂",
                crystal_structure="Tetragonal (distorted antifluorite)",
                space_group="I4₁/acd (No. 142)",
                temperature_range=(0, 1015),
                band_gap=0.0,
                lattice_constants=(12.67, 25.48),
                carrier_density=1e18,
                synthesis_method=["Bridgman growth", "Flux method"],
                commercially_available=False,
                cost_per_gram=None,
                discovery_paper="Liu et al., Nature Materials 13, 677 (2014)"
            ),
        ],
        prototype_material="Cd₃As₂",

        neighboring_phases=["Weyl Semimetal", "Topological Insulator", "Normal Metal"],
        discovery_year=2014,
        theoretical_prediction_year=2012,
        experimental_confirmation_year=2014,
        discovered_by="Wang et al. (theory 2012) / Liu et al. (experiment 2014)",

        key_theoretical_papers=[
            "Wang et al., PRB 85, 195320 (2012) — Na₃Bi prediction",
            "Wang et al., PRB 88, 125427 (2013) — Cd₃As₂ prediction",
        ],
        key_experimental_papers=[
            "Liu et al., Science 343, 864 (2014) — Na₃Bi ARPES",
            "Liu et al., Nature Materials 13, 677 (2014) — Cd₃As₂ ARPES",
            "Neupane et al., Nature Commun. 5, 3786 (2014)",
        ],
        review_papers=[
            "Armitage, Mele, Vishwanath, RMP 90, 015001 (2018)",
        ],
        textbook_references=["Bernevig & Hughes, Ch. 13"],

        technological_applications=[
            "Ultra-high mobility transistors",
            "Topological Hall sensors",
        ],
        potential_applications=[
            "Relativistic electron devices",
            "Topological quantum computing (with proximity-induced SC)",
        ],
        open_questions=[
            "Dirac vs Weyl: can crystal symmetry be broken to split the Dirac point?",
            "Role of electron-electron interactions in 3D Dirac semimetals",
        ],
    ))

    # =========================================================================
    # SPIN GLASS
    # =========================================================================
    registry.register(Phase(
        name="Spin Glass",
        category="Strongly-Correlated",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={ContinuousSymmetry.SO3, SpaceTimeSymmetry.TIME_REVERSAL},
            broken_to={DiscreteSymmetry.Z2},
            order_parameter=OrderParameter(
                name="Edwards-Anderson order parameter",
                symbol="q_EA",
                physical_meaning="Time-averaged local magnetisation squared: q = [<S_i>²]_disorder",
                units="dimensionless",
                symmetry_representation="scalar",
                complex_valued=False,
                field_theory="Replica field theory (SK model)",
                universality_class="Mean-field (SK) or short-range (Edwards-Anderson)",
                measurement_technique=["AC susceptibility", "Neutron spin echo", "μSR"]
            ),
            spontaneous=True,
            universality_class="Edwards-Anderson (short range)",
            num_goldstone_modes=0,
            topological_defects=["Frustration loops"],
        ),

        topology=TopologicalProperties(has_topological_order=False, bulk_gap=False),

        quantum=QuantumProperties(
            berry_phase=0.0,
            quantum_phase_transition=True,
            qpt_universality_class="Quantum spin glass (transverse field Ising)",
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=False,
            far_from_equilibrium=True,
            time_evolution=TimeEvolution(
                ergodic=False,
                chaotic=True,
                thermalization_time=1e6,
            )
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Cusp in AC susceptibility χ(T) at T_g (frequency-dependent)",
                "Remanent magnetisation: ZFC ≠ FC",
                "Slow non-exponential relaxation (stretched exponential)",
                "Memory and rejuvenation effects",
                "Flat neutron scattering (no Bragg peaks, no spin waves)",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Neutron spin echo",
                    energy_range=(0, 1e-3),
                    characteristic_features=[
                        "Quasi-elastic scattering at all Q",
                        "Non-exponential intermediate scattering function",
                    ]
                )
            ],
            transport=TransportSignature(
                hall_coefficient="Anomalous Hall in metallic spin glasses",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="AC susceptibility",
                    measures="χ'(ω,T) cusp at T_g",
                    typical_setup="SQUID, frequencies 0.01-10000 Hz, T = 0.1-300 K"
                ),
                ExperimentalTechnique(
                    name="μSR",
                    measures="Local field distribution, freezing dynamics",
                    typical_setup="Muon beam at ISIS or PSI"
                )
            ],
            temperature_control=(0.01, 300)
        ),

        materials=[
            Material(
                formula="Cu₁₋ₓMnₓ (x ~ 0.01-0.1)",
                crystal_structure="FCC (dilute Mn in Cu host)",
                space_group="Fm-3m (No. 225)",
                temperature_range=(0, 30),
                doping_required="x = 0.01-0.10 Mn",
                synthesis_method=["Melt alloying", "Quenching"],
                commercially_available=True,
                cost_per_gram=0.05,
                discovery_paper="Cannella & Mydosh, PRB 6, 4220 (1972)"
            ),
            Material(
                formula="Fe₀.₅Mn₀.₅TiO₃",
                crystal_structure="Ilmenite (rhombohedral)",
                space_group="R-3 (No. 148)",
                temperature_range=(0, 20),
                synthesis_method=["Solid state reaction", "Float zone"],
                commercially_available=False,
            ),
            Material(
                formula="LiHo₀.₁₆₇Y₀.₈₃₃F₄",
                crystal_structure="Scheelite (tetragonal)",
                space_group="I4₁/a (No. 88)",
                temperature_range=(0, 0.5),
                synthesis_method=["Czochralski"],
                commercially_available=False,
                discovery_paper="Bitko et al., PRL 77, 940 (1996)"
            ),
        ],
        prototype_material="CuMn (canonical metallic spin glass)",

        neighboring_phases=["Paramagnet", "Ferromagnet"],
        discovery_year=1972,
        theoretical_prediction_year=1975,
        experimental_confirmation_year=1972,
        discovered_by="Cannella & Mydosh (1972); Edwards & Anderson (theory 1975)",

        key_theoretical_papers=[
            "Edwards & Anderson, J. Phys. F 5, 965 (1975) — EA model",
            "Sherrington & Kirkpatrick, PRL 35, 1792 (1975) — SK model",
            "Parisi, PRL 43, 1754 (1979) — replica symmetry breaking",
        ],
        key_experimental_papers=[
            "Cannella & Mydosh, PRB 6, 4220 (1972) — first observation",
            "Mezard et al., J. Phys. 45, 843 (1984) — TAP free energy",
        ],
        review_papers=[
            "Binder & Young, RMP 58, 801 (1986)",
            "Mydosh, Spin Glasses: An Experimental Introduction (1993)",
        ],
        textbook_references=["Mezard, Parisi, Virasoro, Spin Glass Theory and Beyond (1987)"],

        technological_applications=[
            "Combinatorial optimisation (spin glass = NP-hard ground state)",
            "Neural network models (Hopfield network = spin glass)",
        ],
        potential_applications=[
            "Quantum annealing / adiabatic quantum computing",
            "Pattern recognition and associative memory",
        ],
        open_questions=[
            "Does replica symmetry breaking survive in finite-dimensional systems?",
            "Is there a true spin glass phase transition in d=3?",
            "Quantum spin glass: exact nature of quantum critical point",
        ],
        controversies=[
            "Droplet model (Fisher-Huse) vs replica symmetry breaking (Parisi): which is correct in d=3?",
        ]
    ))

    # =========================================================================
    # NEMATIC LIQUID CRYSTAL
    # =========================================================================
    registry.register(Phase(
        name="Nematic Liquid Crystal",
        category="Symmetry-Broken",
        dimensionality=3,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={ContinuousSymmetry.SO3},
            broken_to={ContinuousSymmetry.SO2},
            order_parameter=OrderParameter(
                name="Nematic order parameter (tensor)",
                symbol="Q_αβ",
                physical_meaning="Traceless symmetric tensor: Q = S(n⊗n − I/3); S = orientational order parameter",
                units="dimensionless (0 ≤ S ≤ 1)",
                symmetry_representation="tensor",
                complex_valued=False,
                dimension=5,
                field_theory="Frank elastic theory / Landau-de Gennes",
                critical_exponent_beta=0.25,
                universality_class="Mean-field (weakly first order)",
                measurement_technique=["Polarised optical microscopy", "X-ray scattering", "NMR"]
            ),
            spontaneous=True,
            universality_class="Weakly first-order (fluctuation-induced)",
            num_goldstone_modes=2,
            goldstone_dispersion="ω ~ k (director fluctuations / orientational waves)",
            topological_defects=["Disclinations (strength ±1/2)", "Point defects (hedgehogs)"]
        ),

        topology=TopologicalProperties(
            has_topological_order=False,
            bulk_gap=False,
            edge_states=False,
        ),

        quantum=QuantumProperties(
            berry_phase=0.0,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=True)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Optical birefringence (Δn = n_e − n_o ~ 0.1-0.4)",
                "Schlieren textures under crossed polarisers",
                "Weakly first-order isotropic-nematic transition",
                "X-ray scattering: broad liquid-like peak, no 3D order",
                "Freedericksz transition under electric/magnetic field",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Polarised optical microscopy",
                    energy_range=(1.5, 3.5),
                    characteristic_features=[
                        "Schlieren texture with 2- and 4-brush defects",
                        "Birefringent colour fringes",
                        "Uniform alignment in rubbed cells",
                    ]
                ),
                SpectroscopicSignature(
                    technique="X-ray scattering",
                    energy_range=(1000, 100000),
                    characteristic_features=[
                        "Diffuse peak at q ~ 2π/d (molecular length)",
                        "No Bragg peaks (no positional order)",
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="Anisotropic ionic conductivity σ_∥ ≠ σ_⊥",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Polarised optical microscopy",
                    measures="Director field, defect textures, birefringence",
                    typical_setup="Hot stage + crossed polarisers, λ/4 plate"
                ),
                ExperimentalTechnique(
                    name="Freedericksz cell",
                    measures="Elastic constants K₁, K₂, K₃",
                    typical_setup="Rubbed polyimide cell, electric field ~ 1 V/μm"
                )
            ],
            temperature_control=(250, 400)
        ),

        materials=[
            Material(
                formula="5CB (4-cyano-4′-pentylbiphenyl)",
                crystal_structure="Nematic liquid crystal",
                space_group="N/A",
                temperature_range=(295, 308),
                synthesis_method=["Organic synthesis"],
                commercially_available=True,
                cost_per_gram=1.50,
                discovery_paper="Gray et al., Electron. Lett. 9, 130 (1973)"
            ),
            Material(
                formula="MBBA",
                crystal_structure="Nematic LC",
                space_group="N/A",
                temperature_range=(294, 320),
                synthesis_method=["Organic synthesis"],
                commercially_available=True,
                cost_per_gram=2.0
            ),
        ],
        prototype_material="5CB (pentyl cyanobiphenyl)",

        neighboring_phases=["Normal Liquid", "Crystal"],
        discovery_year=1888,
        discovered_by="Reinitzer & Lehmann (1888)",

        key_theoretical_papers=[
            "Landau & de Gennes, The Physics of Liquid Crystals (1974)",
            "Onsager, Ann. N.Y. Acad. Sci. 51, 627 (1949) — hard rod nematic",
            "Frank, Discuss. Faraday Soc. 25, 19 (1958) — elastic theory",
        ],
        key_experimental_papers=[
            "Reinitzer, Monatsh. Chem. 9, 421 (1888) — discovery",
            "Gray et al. (1973) — stable room-temperature nematic (LCD materials)",
        ],
        review_papers=["de Gennes & Prost, The Physics of Liquid Crystals (1993)"],
        textbook_references=["Chaikin & Lubensky, Principles of Condensed Matter Physics (1995)"],

        technological_applications=[
            "LCD displays (every smartphone, monitor, TV)",
            "Spatial light modulators",
            "Optical waveplates and retarders",
        ],
        potential_applications=[
            "Liquid crystal elastomers (soft actuators)",
            "Active matter systems (bacterial suspensions)",
            "Topological photonics with LC defects",
        ],
        open_questions=[
            "Quantum liquid crystals: electronic nematic order in cuprates / URu₂Si₂",
            "Topological defects in 3D active nematics",
        ],
    ))

    # =========================================================================
    # FLOQUET TOPOLOGICAL INSULATOR
    # =========================================================================
    registry.register(Phase(
        name="Floquet Topological Insulator",
        category="Topological",
        dimensionality=2,

        symmetry_breaking=None,

        topology=TopologicalProperties(
            has_topological_order=True,
            topological_order_type="Chern (Floquet)",
            invariants_2d=[
                TopologicalInvariant(
                    name="Floquet Chern number",
                    symbol="C_F",
                    value=1,
                    physical_meaning="Winding of Floquet operator around Brillouin zone; anomalous edge modes survive even when bulk bands trivial",
                    k_theory="K¹(T³) — quasi-energy Brillouin zone is a torus",
                    observable_consequence=[
                        "Chiral Floquet edge states at quasi-energy 0 and π",
                        "Anomalous Floquet phase: edge states with C=0 bulk",
                        "Topological pumping of one quantum of Hall conductance per drive cycle",
                    ],
                    protected_by={"discrete time-translation symmetry (Floquet)"},
                    robust_to_disorder=True,
                    quantization="exact"
                )
            ],
            bulk_gap=True,
            edge_states=True,
            edge_state_dispersion="Floquet edge modes at ε = 0 and ε = ℏΩ/2",
            long_range_entanglement=False,
        ),

        quantum=QuantumProperties(
            berry_phase=np.pi,
            berry_curvature="Berry curvature of Floquet bands",
            entanglement=EntanglementStructure(
                area_law=True,
                long_range_entanglement=False,
                entanglement_entropy_formula="S ~ L  (Floquet edge entropy)",
                tensor_network_structure="PEPS"
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=False,
            time_evolution=TimeEvolution(ergodic=False, integrable=False),
            driven=DrivenDynamics(
                floquet_system=True,
                drive_frequency=6e12,
                floquet_topological_invariant=1,
                anomalous_floquet_phase=True,
                prethermal_regime=True,
            )
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Floquet-Bloch bands observed in ARPES with pump-probe",
                "Chiral edge modes at quasi-energy 0 and π/T",
                "Anomalous Hall response in driven graphene",
                "Topological pumping in optical lattices",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Time-resolved ARPES (tr-ARPES)",
                    energy_range=(-3.0, 3.0),
                    characteristic_features=[
                        "Floquet replica bands separated by ℏΩ",
                        "Gap opening at Dirac point under circularly polarised light",
                        "Floquet-Bloch states in ultrafast pump-probe",
                    ]
                )
            ],
            required_techniques=[
                ExperimentalTechnique(
                    name="tr-ARPES with pump-probe",
                    measures="Floquet band structure, gap opening",
                    typical_setup="Graphene or TI surface + circularly polarised mid-IR pump, 100 fs resolution"
                ),
                ExperimentalTechnique(
                    name="Optical lattice Floquet spectroscopy",
                    measures="Floquet Chern number, edge currents",
                    typical_setup="Cold atoms in laser lattice with periodic modulation"
                )
            ],
            sample_purity_required="Drive frequency >> scattering rate (quasi-static regime)",
            temperature_control=(0.0, 1e-6)
        ),

        materials=[
            Material(
                formula="Graphene + circularly polarised light",
                crystal_structure="Honeycomb monolayer",
                space_group="P6/mmm (No. 191)",
                temperature_range=(0, 300),
                band_gap=0.0,
                synthesis_method=["CVD", "Mechanical exfoliation"],
                commercially_available=False,
                discovery_paper="McIver et al., Nature Physics 16, 38 (2020)"
            ),
            Material(
                formula="Photonic Floquet lattice",
                crystal_structure="Helical waveguide array",
                space_group="N/A",
                temperature_range=(300, 300),
                synthesis_method=["Femtosecond laser writing in glass"],
                commercially_available=False,
                discovery_paper="Rechtsman et al., Nature 496, 196 (2013)"
            ),
        ],
        prototype_material="Graphene under circularly polarised mid-IR drive",

        neighboring_phases=["Topological Insulator", "Weyl Semimetal", "Time Crystal"],
        discovery_year=2013,
        theoretical_prediction_year=2009,
        experimental_confirmation_year=2013,
        discovered_by="Oka & Aoki (theory 2009) / Rechtsman et al. (photonics 2013) / McIver et al. (graphene 2020)",

        key_theoretical_papers=[
            "Oka & Aoki, PRB 79, 081406 (2009) — graphene prediction",
            "Kitagawa et al., PRB 82, 235114 (2010) — Floquet TI classification",
            "Rudner et al., PRX 3, 031005 (2013) — anomalous Floquet phase",
        ],
        key_experimental_papers=[
            "Rechtsman et al., Nature 496, 196 (2013) — photonic realisation",
            "Jotzu et al., Nature 515, 237 (2014) — cold atoms",
            "McIver et al., Nature Physics 16, 38 (2020) — graphene Hall",
        ],
        review_papers=[
            "Oka & Kitamura, Annu. Rev. Condens. Matter Phys. 10, 387 (2019)",
        ],
        textbook_references=["Bukov, D'Alessio, Polkovnikov, Adv. Phys. 64, 139 (2015)"],

        technological_applications=[
            "Optically-controlled topological switches",
            "Laser-driven topological lasers",
        ],
        potential_applications=[
            "Light-induced superconductivity control",
            "Floquet quantum computing",
        ],
        open_questions=[
            "Heating problem: how to access Floquet steady state without thermalising?",
            "Anomalous Floquet phase in 3D materials?",
            "Interaction effects in Floquet topological phases",
        ],
    ))

    # =========================================================================
    # WIGNER CRYSTAL
    # =========================================================================
    registry.register(Phase(
        name="Wigner Crystal",
        category="Strongly-Correlated",
        dimensionality=2,

        symmetry_breaking=SymmetryBreakingPattern(
            original_symmetry={SpaceTimeSymmetry.TRANSLATION, SpaceTimeSymmetry.ROTATION},
            broken_to={DiscreteSymmetry.D6},
            order_parameter=OrderParameter(
                name="Charge density wave amplitude",
                symbol="ρ_G",
                physical_meaning="Fourier component of electron density at reciprocal lattice vector G",
                units="electrons/cm²",
                symmetry_representation="scalar",
                complex_valued=True,
                field_theory="Hartree-Fock / Wigner lattice",
                universality_class="2D melting (Kosterlitz-Thouless-Halperin-Nelson-Young)",
                measurement_technique=["Microwave pinning resonance", "Transport", "STM"]
            ),
            spontaneous=True,
            universality_class="2D melting (KTHNY theory)",
            critical_field=3.0,
            num_goldstone_modes=2,
            goldstone_dispersion="ω ~ k^(1/2)  (2D plasmon / phonon, r_s-dependent)",
            topological_defects=["Dislocations", "Disclinations (2D melting)"]
        ),

        topology=TopologicalProperties(has_topological_order=False, bulk_gap=True),

        quantum=QuantumProperties(
            berry_phase=0.0,
            quantum_fluctuations_suppress_order=True,
            entanglement=EntanglementStructure(
                area_law=True,
                short_range_entanglement=True,
            )
        ),

        dynamics=DynamicalProperties(
            equilibrium=True,
            time_evolution=TimeEvolution(ergodic=False)
        ),

        experimental=ExperimentalCharacterization(
            primary_signatures=[
                "Microwave pinning mode resonance (sharp peak in Re σ(ω))",
                "Insulating transport at very low n (high r_s)",
                "Threshold electric field for depinning",
                "STM imaging of triangular electron lattice in 2D",
                "Reentrant insulating phase at high B in 2DEG",
            ],
            spectroscopy=[
                SpectroscopicSignature(
                    technique="Microwave spectroscopy",
                    energy_range=(0, 0.01),
                    characteristic_features=[
                        "Broad pinning mode resonance ~ 1 GHz",
                        "Mode stiffens with increasing B",
                    ]
                ),
                SpectroscopicSignature(
                    technique="STM",
                    energy_range=(-0.1, 0.1),
                    characteristic_features=[
                        "Triangular charge density modulation",
                        "Wigner-Seitz cell visible in LDOS",
                    ]
                )
            ],
            transport=TransportSignature(
                conductivity="Insulating at r_s >> 1; pinned WC has zero DC conductivity",
                hall_coefficient="Hall insulator behaviour",
            ),
            required_techniques=[
                ExperimentalTechnique(
                    name="Microwave resonance spectroscopy",
                    measures="Pinning mode frequency, melting transition",
                    typical_setup="GaAs/AlGaAs 2DEG, B > 1 T, T < 100 mK, coplanar waveguide"
                ),
                ExperimentalTechnique(
                    name="STM on 2D material",
                    measures="Real-space charge density",
                    typical_setup="MoSe₂ or WSe₂ moiré, T < 4 K, UHV STM"
                )
            ],
            sample_purity_required="Ultra-high mobility μ > 10⁷ cm²/Vs (GaAs) or clean moiré",
            temperature_control=(0.01, 1.0)
        ),

        materials=[
            Material(
                formula="GaAs/AlGaAs (low n, high B)",
                crystal_structure="2DEG in heterostructure",
                space_group="F-43m (No. 216)",
                temperature_range=(0, 0.5),
                carrier_density=3e10,
                synthesis_method=["MBE (ultra-high purity)"],
                commercially_available=False,
                discovery_paper="Andrei et al., PRL 60, 2765 (1988)"
            ),
            Material(
                formula="MoSe₂/WSe₂ moiré",
                crystal_structure="Moiré superlattice",
                space_group="N/A",
                temperature_range=(0, 30),
                synthesis_method=["Mechanical stacking of monolayers"],
                commercially_available=False,
                discovery_paper="Xu et al., Nature 587, 214 (2020)"
            ),
        ],
        prototype_material="GaAs/AlGaAs 2DEG in high magnetic field",

        neighboring_phases=["Fractional Quantum Hall State", "Integer Quantum Hall State", "Normal Metal"],
        discovery_year=1934,
        theoretical_prediction_year=1934,
        experimental_confirmation_year=1988,
        discovered_by="Wigner (theory 1934) / Andrei et al. (experiment 1988)",

        key_theoretical_papers=[
            "Wigner, Phys. Rev. 46, 1002 (1934) — original prediction",
            "Tanatar & Ceperley, PRB 39, 5005 (1989) — QMC phase diagram, r_s = 37",
            "Halperin, Nelson, Young, PRB 19, 2457 (1979) — KTHNY 2D melting",
        ],
        key_experimental_papers=[
            "Andrei et al., PRL 60, 2765 (1988) — first pinning mode observation",
            "Xu et al., Nature 587, 214 (2020) — Wigner crystal in moiré TMD",
        ],
        review_papers=[
            "Monarkha & Kono, Two-Dimensional Coulomb Liquids and Solids (2004)",
        ],
        textbook_references=["Giuliani & Vignale, Quantum Theory of the Electron Liquid (2005)"],

        technological_applications=[
            "Resistance standard candidate (complementary to QHE)",
        ],
        potential_applications=[
            "Electron qubits in a Wigner crystal lattice",
            "Strongly correlated electron simulator",
        ],
        open_questions=[
            "Quantum melting of 2D Wigner crystal: r_s at transition?",
            "Competition between Wigner crystal and FQHE at same filling factor",
            "3D Wigner crystal: does it exist in bulk at accessible densities?",
        ],
    ))

    # =========================================================================
    # PHASE TRANSITIONS (Graph)
    # =========================================================================
    registry.register_transition(PhaseTransition(
        phase_from="Crystal",
        phase_to="Normal Liquid",
        order=1,
        continuous=False,
        control_parameter="temperature",
        critical_value=1687.0,   # Si melting point K
        mechanism="Melting: thermal fluctuations overcome lattice energy",
        order_parameter_changes="Density wave ρ(r) → uniform ρ",
        symmetry_changes="Discrete translation restored",
        latent_heat=50.2e3,   # J/mol Si
        hysteresis=True,
        phase_coexistence=True,
        experimental_signatures=["Latent heat peak in DSC", "Sharp Bragg peak disappearance"]
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Ferromagnet",
        phase_to="Paramagnet",
        order=2,
        continuous=True,
        control_parameter="temperature",
        critical_value=1043.0,   # Fe Curie point
        universality_class="3D Heisenberg",
        critical_exponents={"β": 0.365, "γ": 1.386, "ν": 0.705, "η": 0.033},
        mechanism="Thermal fluctuations disorder spin alignment",
        order_parameter_changes="M → 0 continuously",
        symmetry_changes="SO(3) restored",
        critical_slowing_down=True,
        relaxation_time_divergence="τ ~ ξ^z, z ≈ 2",
        experimental_signatures=["Divergent susceptibility χ ~ |T-T_c|^(-γ)", "Specific heat anomaly"]
    ))

    registry.register_transition(PhaseTransition(
        phase_from="BCS Superconductor",
        phase_to="Normal Metal",
        order=2,
        continuous=True,
        control_parameter="temperature",
        critical_value=9.2,   # Nb T_c
        universality_class="Mean-field (3D XY for fluctuations)",
        critical_exponents={"β": 0.5, "γ": 1.0, "ν": 0.5},
        mechanism="Cooper pairs break up due to thermal fluctuations",
        order_parameter_changes="Δ → 0 continuously",
        symmetry_changes="U(1) gauge symmetry restored",
        latent_heat=0.0,
        critical_slowing_down=True,
        experimental_signatures=["Jump in specific heat at T_c", "Resistance onset"]
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Mott Insulator",
        phase_to="BCS Superconductor",
        order=2,
        continuous=True,
        control_parameter="doping",
        critical_value=0.16,  # Optimal doping in cuprates (holes per Cu)
        universality_class="Unknown (central puzzle of cuprates)",
        mechanism="Doped holes in Mott insulator form Cooper pairs via spin fluctuations",
        order_parameter_changes="Mott gap closes, SC gap opens",
        symmetry_changes="U(1) broken, AF order destroyed",
        experimental_signatures=["Dome-shaped T_c vs doping", "Pseudogap above T_c"]
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Bose-Einstein Condensate",
        phase_to="Normal Bose Gas",
        order=2,
        continuous=True,
        control_parameter="temperature",
        critical_value=170e-9,   # ~170 nK for ⁸⁷Rb
        universality_class="3D XY",
        critical_exponents={"β": 0.349, "ν": 0.672},
        mechanism="Thermal depletion of condensate fraction",
        order_parameter_changes="Ψ = √n₀ e^(iφ) → 0",
        symmetry_changes="U(1) phase symmetry restored",
        experimental_signatures=["Bimodal → thermal distribution in TOF", "Loss of interference"]
    ))


    # New transitions for new phases
    registry.register_transition(PhaseTransition(
        phase_from="Paramagnet",
        phase_to="Ferromagnet",
        order=2,
        continuous=True,
        control_parameter="temperature",
        critical_value=1043.0,
        universality_class="3D Heisenberg",
        critical_exponents={"beta": 0.365, "gamma": 1.386, "nu": 0.705},
        mechanism="Thermal fluctuations order spins below Curie temperature",
        order_parameter_changes="M: 0 -> finite",
        symmetry_changes="SO(3) broken to SO(2)",
        experimental_signatures=["Divergent susceptibility", "Specific heat anomaly"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Normal Metal",
        phase_to="Topological Insulator",
        order=2,
        continuous=True,
        control_parameter="spin-orbit coupling strength",
        critical_value=0.0,
        universality_class="3D Z2 topological transition",
        mechanism="Band inversion at TRIM point driven by spin-orbit coupling",
        order_parameter_changes="Z2 invariant: 0 -> 1",
        symmetry_changes="No symmetry change — purely topological",
        experimental_signatures=["Gap closing and reopening in ARPES", "Surface state appearance"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Normal Metal",
        phase_to="Spin Glass",
        order=2,
        continuous=True,
        control_parameter="temperature",
        critical_value=30.0,
        universality_class="Edwards-Anderson",
        mechanism="Freezing of randomly interacting spins below T_g",
        order_parameter_changes="q_EA: 0 -> finite",
        symmetry_changes="Time-reversal broken in frozen spin configuration",
        experimental_signatures=["AC susceptibility cusp", "ZFC-FC splitting"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Normal Liquid",
        phase_to="Nematic Liquid Crystal",
        order=1,
        continuous=False,
        control_parameter="temperature",
        critical_value=308.0,
        universality_class="Weakly first-order (fluctuation-induced)",
        mechanism="Orientational ordering of anisotropic molecules",
        order_parameter_changes="Q_ab: 0 -> finite (S ~ 0.4-0.7)",
        symmetry_changes="SO(3) broken to D_inf_h",
        latent_heat=1000.0,
        hysteresis=True,
        experimental_signatures=["Birefringence onset", "Schlieren texture"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Integer Quantum Hall State",
        phase_to="Fractional Quantum Hall State",
        order=2,
        continuous=True,
        control_parameter="magnetic field",
        critical_value=10.0,
        universality_class="Unknown — plateau-to-plateau transition",
        mechanism="Electron-electron interactions drive Laughlin correlated state",
        order_parameter_changes="sigma_xy: e^2/h -> e^2/(3h) (nu=1/3)",
        symmetry_changes="No symmetry change — emergent composite fermion statistics",
        experimental_signatures=["sigma_xy plateau at fractional filling", "sigma_xx -> 0"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Dirac Semimetal",
        phase_to="Topological Insulator",
        order=2,
        continuous=True,
        control_parameter="chemical potential / strain",
        critical_value=0.0,
        universality_class="3D Z2 topological",
        mechanism="Opening of gap at Dirac point by symmetry breaking (magnetic or strain)",
        order_parameter_changes="Z2: 0 -> 1",
        symmetry_changes="Inversion or time-reversal broken at Dirac point",
        experimental_signatures=["Gap opening in ARPES", "Surface state connectivity change"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Dirac Semimetal",
        phase_to="Weyl Semimetal",
        order=2,
        continuous=True,
        control_parameter="magnetic field or strain",
        critical_value=0.0,
        universality_class="Lifshitz transition",
        mechanism="TRS or inversion breaking splits 4-fold Dirac into 2x Weyl nodes",
        order_parameter_changes="Chirality quantum number: 0 -> +/-1",
        symmetry_changes="Time-reversal or inversion symmetry broken",
        experimental_signatures=["Fermi arc splitting", "Anomalous Hall onset"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Wigner Crystal",
        phase_to="Fractional Quantum Hall State",
        order=1,
        continuous=False,
        control_parameter="filling factor nu",
        critical_value=0.2,
        universality_class="Unknown",
        mechanism="At nu ~ 1/5, competition between WC and Laughlin liquid",
        order_parameter_changes="Positional order destroyed, topological order established",
        symmetry_changes="Translation symmetry restored; emergent gauge symmetry",
        hysteresis=True,
        experimental_signatures=["Reentrant insulating phase", "Microwave resonance disappears at nu=1/5"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="BCS Superconductor",
        phase_to="Topological Superconductor",
        order=2,
        continuous=True,
        control_parameter="chemical potential / magnetic field",
        critical_value=2.0,
        universality_class="Class D Ising",
        mechanism="Zeeman field + SOC drives BCS into topological phase with Majorana modes",
        order_parameter_changes="Z2 invariant: 0 -> 1 (gap remains finite)",
        symmetry_changes="No new symmetry broken — purely topological",
        experimental_signatures=["ZBCP emergence", "4pi Josephson effect onset"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Topological Insulator",
        phase_to="Floquet Topological Insulator",
        order=2,
        continuous=True,
        control_parameter="drive amplitude",
        critical_value=0.0,
        universality_class="Floquet Z2 / Chern",
        mechanism="Periodic drive induces Floquet-Bloch bands with higher Chern number",
        order_parameter_changes="Floquet Chern number: 0 -> 1",
        symmetry_changes="Continuous time-translation -> discrete (Floquet) time-translation",
        experimental_signatures=["Floquet sidebands in tr-ARPES", "Anomalous Hall onset"],
    ))


    # Orphan phase connections
    registry.register_transition(PhaseTransition(
        phase_from="Quantum Spin Liquid",
        phase_to="Mott Insulator",
        order=2,
        continuous=True,
        control_parameter="pressure / frustration",
        critical_value=0.0,
        universality_class="Deconfined quantum criticality",
        mechanism="Spinon confinement under pressure collapses QSL into Mott insulator",
        order_parameter_changes="Z2 topological order destroyed; magnetic order may appear",
        symmetry_changes="Emergent gauge symmetry lost",
        experimental_signatures=["Disappearance of QSL signatures", "Possible AFM order onset"],
    ))

    registry.register_transition(PhaseTransition(
        phase_from="Time Crystal",
        phase_to="Floquet Topological Insulator",
        order=2,
        continuous=True,
        control_parameter="disorder strength",
        critical_value=2.0,
        universality_class="MBL-to-Floquet topological",
        mechanism="Reducing disorder in driven MBL system allows Floquet band topology to emerge",
        order_parameter_changes="Time-translation symmetry breaking -> Floquet Chern number",
        symmetry_changes="Discrete time-translation restored at Floquet level",
        experimental_signatures=["Edge mode appearance", "Loss of subharmonic response"],
    ))

    return registry
