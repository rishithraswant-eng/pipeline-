import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useSessionStore } from '../store/sessionStore';

const NetworkGraph = () => {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const topology = useSessionStore((state) => state.topology);
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: null });

  useEffect(() => {
    if (!containerRef.current || !topology.nodes || topology.nodes.length === 0) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // ─── Defs: gradients & filters ───────────────────────────────────────────
    const defs = svg.append("defs");

    // Background gradient (top: light lavender, bottom: white/pinkish)
    const bgGrad = defs.append("linearGradient")
      .attr("id", "bgGradient")
      .attr("x1", "0%").attr("y1", "0%")
      .attr("x2", "30%").attr("y2", "100%");
    bgGrad.append("stop").attr("offset", "0%").attr("stop-color", "#DDE4F5");
    bgGrad.append("stop").attr("offset", "60%").attr("stop-color", "#EEF1FB");
    bgGrad.append("stop").attr("offset", "100%").attr("stop-color", "#F5F0FC");

    // Default node gradient (3D sphere effect: blue-gray)
    const nodeGrad = defs.append("radialGradient")
      .attr("id", "nodeGrad")
      .attr("cx", "35%").attr("cy", "30%").attr("r", "65%");
    nodeGrad.append("stop").attr("offset", "0%").attr("stop-color", "#7E92B8");
    nodeGrad.append("stop").attr("offset", "100%").attr("stop-color", "#3A4D6E");

    // DC node gradient (purple sphere)
    const dcGrad = defs.append("radialGradient")
      .attr("id", "dcGrad")
      .attr("cx", "35%").attr("cy", "30%").attr("r", "65%");
    dcGrad.append("stop").attr("offset", "0%").attr("stop-color", "#B97BF5");
    dcGrad.append("stop").attr("offset", "100%").attr("stop-color", "#5B21B6");

    // Glow filter for DC nodes
    const dcGlow = defs.append("filter").attr("id", "dcGlow");
    dcGlow.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", "4").attr("result", "blur");
    const feMerge = dcGlow.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "blur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Subtle drop shadow for regular nodes
    const shadow = defs.append("filter").attr("id", "nodeShadow").attr("x", "-30%").attr("y", "-30%").attr("width", "160%").attr("height", "160%");
    shadow.append("feDropShadow")
      .attr("dx", "0").attr("dy", "2")
      .attr("stdDeviation", "3")
      .attr("flood-color", "#8090C0")
      .attr("flood-opacity", "0.35");

    // ─── Background rect ────────────────────────────────────────────────────
    svg.append("rect")
      .attr("width", width).attr("height", height)
      .attr("fill", "url(#bgGradient)");

    // ─── Scattered star/dot particles ───────────────────────────────────────
    const particleGroup = svg.append("g").attr("class", "particles");
    const numParticles = 40;
    for (let i = 0; i < numParticles; i++) {
      const x = Math.random() * width;
      const y = Math.random() * height * 0.85;
      const r = Math.random() * 2.2 + 0.4;
      const opacity = Math.random() * 0.4 + 0.1;
      particleGroup.append("circle")
        .attr("cx", x).attr("cy", y)
        .attr("r", r)
        .attr("fill", "#8890CC")
        .attr("opacity", opacity);
    }

    // ─── Wavy bottom fog ────────────────────────────────────────────────────
    const waveFogGrad = defs.append("linearGradient")
      .attr("id", "waveFog")
      .attr("x1", "0%").attr("y1", "0%")
      .attr("x2", "0%").attr("y2", "100%");
    waveFogGrad.append("stop").attr("offset", "0%").attr("stop-color", "#C8C0E8").attr("stop-opacity", "0");
    waveFogGrad.append("stop").attr("offset", "100%").attr("stop-color", "#C8C0E8").attr("stop-opacity", "0.5");

    // Simple wave path at the bottom
    const waveY = height * 0.75;
    const waveAmp = 22;
    const waveFreq = width / 3;
    let wavePath = `M0,${waveY}`;
    for (let x = 0; x <= width; x += 4) {
      const y = waveY + Math.sin((x / waveFreq) * Math.PI * 2) * waveAmp
               + Math.sin((x / (waveFreq * 0.6)) * Math.PI * 2) * (waveAmp * 0.4);
      wavePath += ` L${x},${y}`;
    }
    wavePath += ` L${width},${height} L0,${height} Z`;

    svg.append("path")
      .attr("d", wavePath)
      .attr("fill", "url(#waveFog)");

    // ─── Force simulation ────────────────────────────────────────────────────
    const zoom = d3.zoom().scaleExtent([0.15, 4]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom);

    const g = svg.append("g");

    const nodes = topology.nodes.map(d => ({ ...d }));
    const edges = topology.edges.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(edges).id(d => d.id).distance(90))
      .force("charge", d3.forceManyBody().strength(-280))
      .force("center", d3.forceCenter(width / 2, height * 0.45))
      .force("collide", d3.forceCollide().radius(32));

    // ─── Links (cyan/teal thin lines) ───────────────────────────────────────
    const link = g.append("g")
      .selectAll("line")
      .data(edges)
      .join("line")
      .attr("stroke", "#9BB8D4")
      .attr("stroke-opacity", 0.55)
      .attr("stroke-width", 1.5);

    // ─── Nodes ───────────────────────────────────────────────────────────────
    const isDC = (d) => d.role === 'Domain Controller' || d.role === 'Crown Jewel';

    const nodeGroup = g.append("g").selectAll("g.node")
      .data(nodes)
      .join("g")
      .attr("class", "node")
      .style("cursor", "pointer")
      .on("mouseover", (event, d) => {
        const rect = containerRef.current.getBoundingClientRect();
        setTooltip({ visible: true, x: event.clientX - rect.left + 14, y: event.clientY - rect.top + 14, content: d });
      })
      .on("mouseout", () => setTooltip(prev => ({ ...prev, visible: false })));

    // Outer glow ring for DC nodes
    nodeGroup.filter(d => isDC(d))
      .append("circle")
      .attr("r", 20)
      .attr("fill", "none")
      .attr("stroke", "#8B5CF6")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.4)
      .attr("filter", "url(#dcGlow)");

    // Main circle
    nodeGroup.append("circle")
      .attr("r", d => isDC(d) ? 14 : 10)
      .attr("fill", d => isDC(d) ? "url(#dcGrad)" : "url(#nodeGrad)")
      .attr("filter", d => isDC(d) ? "url(#dcGlow)" : "url(#nodeShadow)")
      .attr("stroke", d => isDC(d) ? "#9B6BDB" : "#5A6E94")
      .attr("stroke-width", 1.2)
      .attr("stroke-opacity", 0.6);

    // Highlight dot (top-left glint for 3D sphere)
    nodeGroup.append("circle")
      .attr("r", d => isDC(d) ? 4 : 3)
      .attr("cx", d => isDC(d) ? -5 : -3.5)
      .attr("cy", d => isDC(d) ? -5 : -3.5)
      .attr("fill", "rgba(255,255,255,0.55)")
      .attr("pointer-events", "none");

    // ─── Labels ──────────────────────────────────────────────────────────────
    const labels = g.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text(d => d.hostname || d.ip)
      .attr("font-size", "11px")
      .attr("font-family", "'Inter', sans-serif")
      .attr("fill", "#3A4A6E")
      .attr("font-weight", "500")
      .attr("dx", d => isDC(d) ? 20 : 16)
      .attr("dy", 4)
      .attr("pointer-events", "none");

    // ─── Tick ────────────────────────────────────────────────────────────────
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);

      nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);
      labels.attr("x", d => d.x).attr("y", d => d.y);
    });

    return () => simulation.stop();
  }, [topology]);

  if (!topology || !topology.nodes || topology.nodes.length === 0) {
    return (
      <div style={{
        width: '100%', height: '100%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, #DDE4F5 0%, #EEF1FB 60%, #F5F0FC 100%)',
        color: '#6070A0', fontSize: '14px'
      }}>
        Initializing network topology...
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%', display: 'block' }} />

      {tooltip.visible && tooltip.content && (
        <div style={{
          position: 'absolute',
          left: tooltip.x, top: tooltip.y,
          background: 'rgba(255,255,255,0.92)',
          border: '1px solid #C8D0E8',
          borderRadius: '8px',
          padding: '8px 12px',
          pointerEvents: 'none',
          boxShadow: '0 4px 20px rgba(80,100,160,0.18)',
          zIndex: 10,
          color: '#1E2A4A',
          fontSize: '12px',
          backdropFilter: 'blur(8px)'
        }}>
          <div style={{ fontWeight: 700, color: '#5B4BCC', marginBottom: '4px' }}>{tooltip.content.hostname}</div>
          <div style={{ color: '#6070A0' }}>IP: <span style={{ color: '#1E2A4A', fontFamily: 'monospace' }}>{tooltip.content.ip}</span></div>
          <div style={{ color: '#6070A0' }}>Role: <span style={{ color: '#1E2A4A' }}>{tooltip.content.role}</span></div>
          {tooltip.content.services && tooltip.content.services.length > 0 && (
            <div style={{ color: '#6070A0', marginTop: '4px' }}>
              Services: <span style={{ color: '#1E2A4A' }}>{tooltip.content.services.join(', ')}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NetworkGraph;
