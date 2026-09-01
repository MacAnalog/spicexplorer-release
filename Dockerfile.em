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
# QCSXCAD (Qt GUI viewer) is skipped: the lane runs headless.
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
        cython numpy h5py matplotlib gdspy pyyaml scikit-rf "klayout>=0.30"
ENV PATH=/opt/emenv/bin:$PATH

# openEMS from source (no usable package). -fpermissive: CSXCAD vs CGAL headers.
RUN git clone --recursive --depth 1 \
        https://github.com/thliebig/openEMS-Project.git /opt/src/openEMS-Project \
    && cd /opt/src/openEMS-Project \
    && CXXFLAGS="-fpermissive" ./update_openEMS.sh /opt/openems --python || true \
    && CSXCAD_INSTALL_PATH=/opt/openems /opt/emenv/bin/pip install \
        --no-build-isolation ./CSXCAD/python ./openEMS/python \
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
