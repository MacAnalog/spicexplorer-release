# Managed by the private release infra (scripts/release/repo/) — edit there,
# not here; the next port overwrites this file.
# =============================================================================
# EM toolchain image — openEMS (FDTD) built from source + the IHP PDK's own
# openEMS workflow, for the spicexplorer_layout.em verification lane.
#
#   docker compose --profile em build em
#   docker compose run --rm em bash          # toolchain + PDK workflow inside
#
# Deliberately NOT part of spice-base/api: the EM stack (boost/vtk/CGAL + a
# C++ build) is heavy and only needed when verifying reflection/balance
# claims against full-wave results — never in the optimizer loop.
#
# Debian bookworm ships CGAL 5.5 — CGAL 6 breaks CSXCAD, so apt is the pin.
# QCSXCAD (Qt GUI viewer) is skipped via --disable-GUI: the lane runs headless,
# and upstream defaults to GUI=YES, which needs the qtbase5-dev +
# libvtk9-qt-dev stack this image deliberately does not carry.
# =============================================================================
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates \
        libboost-all-dev libhdf5-dev libvtk9-dev libcgal-dev libtinyxml-dev \
        python3 python3-dev python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# python deps in a venv (PEP 668: bookworm's system python is externally managed)
RUN python3 -m venv /opt/emenv \
    && /opt/emenv/bin/pip install --no-cache-dir \
        setuptools wheel setuptools-scm \
        cython numpy h5py matplotlib gdspy pyyaml scikit-rf "klayout>=0.30"
ENV PATH=/opt/emenv/bin:$PATH

# openEMS from source (no usable package). -fpermissive: CSXCAD vs CGAL headers.
#
# --disable-GUI: upstream defaults to GUI=YES and fails the C++ build against a
#   Qt stack this image does not install.
# --skip-dep-check: the checker looks for apt python3-* packages, but our python
#   deps live in the venv above, which is first on PATH. Its warning is noise
#   here; the build itself uses the venv interpreter.
# NO `|| true`: it swallowed the real make failure and let the run die later on a
#   confusing pip error instead. On failure, print the build log the script
#   otherwise keeps to itself inside the image — a red CI run has to be
#   diagnosable from the CI output alone.
#
# `--python` already builds and installs the extensions via
# scripts/build_python.sh; the pip step below is a fallback for the case where
# that does not land them in the venv.
RUN git clone --recursive --depth 1 \
        https://github.com/thliebig/openEMS-Project.git /opt/src/openEMS-Project \
    && cd /opt/src/openEMS-Project \
    && { CXXFLAGS="-fpermissive" ./update_openEMS.sh /opt/openems \
             --python --disable-GUI --skip-dep-check \
         || { echo "=== openEMS build log (tail) ==="; \
              tail -n 200 build_*.log 2>/dev/null || echo "(no build log written)"; \
              exit 1; }; } \
    && { /opt/emenv/bin/python -c "import CSXCAD, openEMS" 2>/dev/null \
         || CSXCAD_INSTALL_PATH=/opt/openems /opt/emenv/bin/pip install \
                --no-build-isolation ./CSXCAD/python ./openEMS/python; } \
    && /opt/emenv/bin/python -c "import CSXCAD, openEMS" \
    && rm -rf /opt/src/openEMS-Project
ENV LD_LIBRARY_PATH=/opt/openems/lib

# the PDK's openEMS workflow + stackup (sparse checkout — the vendored PDK
# subset in platform/docker/pdk/ has no libs.tech/openems)
RUN git clone --filter=blob:none --sparse --depth 1 \
        https://github.com/IHP-GmbH/IHP-Open-PDK.git /opt/src/ihp-pdk \
    && cd /opt/src/ihp-pdk \
    && git sparse-checkout set ihp-sg13g2/libs.tech/openems \
    && mkdir -p /opt/pdk/ihp-sg13g2/libs.tech \
    && cp -r ihp-sg13g2/libs.tech/openems /opt/pdk/ihp-sg13g2/libs.tech/ \
    && rm -rf /opt/src/ihp-pdk
ENV PDK_ROOT=/opt/pdk PDK=ihp-sg13g2

WORKDIR /work
CMD ["bash"]
