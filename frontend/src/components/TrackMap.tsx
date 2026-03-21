import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Props {
  // A map of driver code to progress and color
  positions: Record<string, { progress: number, color: string }>;
}

const TrackMap: React.FC<Props & { circuitPath?: string }> = ({ positions, circuitPath }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const trackPathDrawn = useRef<string | null>(null);

  useEffect(() => {
    console.log('[TrackMap] positions:', positions);
    console.log('[TrackMap] circuitPath:', circuitPath?.substring(0, 50) + '...');
    if (!svgRef.current || !circuitPath) return;
    
    const svg = d3.select(svgRef.current);
    const width = 400;
    const height = 400;
    
    // Only re-draw the static track if the path actually changed
    if (trackPathDrawn.current !== circuitPath) {
      svg.selectAll('*').remove();
      
      svg.attr('viewBox', `0 0 ${width} ${height}`)
         .style('width', '100%')
         .style('height', '100%');

      const container = svg.append('g').attr('class', 'main-container');
      const trackLayer = container.append('g').attr('class', 'track-layer');
      const startLineLayer = container.append('g').attr('class', 'start-line-layer');
      const carsLayer = container.append('g').attr('class', 'cars-layer');

      // Draw shadow path
      trackLayer.append('path')
        .attr('d', circuitPath)
        .attr('fill', 'none')
        .attr('stroke', '#1A1A1D')
        .attr('stroke-width', 16)
        .attr('stroke-linejoin', 'round');

      // Draw main path
      trackLayer.append('path')
        .attr('class', 'circuit-path-node')
        .attr('d', circuitPath)
        .attr('fill', 'none')
        .attr('stroke', '#E10600')
        .attr('stroke-width', 3)
        .attr('stroke-linejoin', 'round')
        .style('filter', 'drop-shadow(0 0 8px rgba(225, 6, 0, 0.6))');

      // Add Start/Finish line
      const pathNode = svg.select('.circuit-path-node').node() as SVGPathElement;
      if (pathNode) {
        const startPoint = pathNode.getPointAtLength(0);
        const nextPoint = pathNode.getPointAtLength(2);
        const angle = Math.atan2(nextPoint.y - startPoint.y, nextPoint.x - startPoint.x);
        const nx = Math.sin(angle);
        const ny = -Math.cos(angle);

        startLineLayer.append('line')
          .attr('x1', startPoint.x - nx * 10).attr('y1', startPoint.y - ny * 10)
          .attr('x2', startPoint.x + nx * 10).attr('y2', startPoint.y + ny * 10)
          .attr('stroke', 'white').attr('stroke-width', 4).attr('stroke-dasharray', '2,2');

        startLineLayer.append('text')
          .attr('x', startPoint.x - nx * 20).attr('y', startPoint.y - ny * 20)
          .attr('fill', 'white').attr('font-size', '10px').attr('font-weight', 'bold')
          .attr('text-anchor', 'middle').text('S/F');
      }

      trackPathDrawn.current = circuitPath;
    }

    // Dynamic car updates
    const carsLayer = svg.select('.cars-layer');
    const pathNode = svg.select('.circuit-path-node').node() as SVGPathElement;
    if (!pathNode) return;

    const totalLength = pathNode.getTotalLength();
    const drivers = Object.entries(positions)
      .sort((a, b) => a[1].progress - b[1].progress); // Higher progress drawn last (on top)

    const carGroups = carsLayer.selectAll<SVGGElement, [string, any]>('.car-group')
      .data(drivers, d => d[0]);

    // JOIN Pattern
    const carEnter = carGroups.enter().append('g')
      .attr('class', 'car-group');

    carEnter.append('circle')
      .attr('r', 7)
      .attr('stroke', '#FFF')
      .attr('stroke-width', 2);

    carEnter.append('text')
      .attr('y', -12)
      .attr('text-anchor', 'middle')
      .attr('fill', '#FFF')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold');

    const merged = carEnter.merge(carGroups);

    merged.select('circle')
      .attr('fill', d => d[1].color)
      .style('filter', d => `drop-shadow(0 0 5px ${d[1].color})`);

    merged.select('text').text(d => d[0]);

    merged.transition()
      .duration(200)
      .ease(d3.easeLinear)
      .attr('transform', d => {
        const progress = isNaN(d[1].progress) ? 0 : d[1].progress;
        const point = pathNode.getPointAtLength(progress * totalLength);
        return `translate(${point.x}, ${point.y})`;
      });

    carGroups.exit().remove();

  }, [positions, circuitPath]);

  return (
    <div className="w-full h-full flex items-center justify-center p-2">
      <div className="w-full h-full flex items-center justify-center relative">
         <svg ref={svgRef} className="w-full h-full max-h-full"></svg>
      </div>
    </div>
  );
};

export default TrackMap;
