import React, { useState } from 'react';
import * as d3 from 'd3';

const SankeyDiagram = () => {
  const [showDetails, setShowDetails] = useState(false);
  
  // Sankey diagram data
  const data = {
    nodes: [
      { name: "Package Arrival" },
      { name: "Assignment" },
      { name: "Locker Storage" },
      { name: "Amazon" },
      { name: "USPS" },
      { name: "UPS" },
      { name: "FedEx" },
      { name: "Other Carriers" },
      { name: "Delivery/Pickup" }
    ],
    links: [
      { source: 0, target: 1, value: 6888 },
      { source: 1, target: 2, value: 6888 },
      { source: 2, target: 3, value: 3524 },
      { source: 2, target: 4, value: 2089 },
      { source: 2, target: 5, value: 667 },
      { source: 2, target: 6, value: 373 },
      { source: 2, target: 7, value: 235 },
      { source: 3, target: 8, value: 3524 },
      { source: 4, target: 8, value: 2089 },
      { source: 5, target: 8, value: 667 },
      { source: 6, target: 8, value: 373 },
      { source: 7, target: 8, value: 235 }
    ]
  };
  
  // Processing times data
  const processingTimes = {
    "Amazon": 33.7,
    "USPS": 103.9,
    "UPS": 68.3,
    "FedEx": 54.5,
    "Other": 172.4
  };
  
  // Locker bank utilization
  const lockerBanks = {
    "Bank 8": 1052,
    "Bank 5": 1046,
    "Bank 6": 1037,
    "Bank 2": 1000,
    "Bank 7": 994,
    "Bank 3": 909,
    "Bank 4": 425,
    "Bank 1": 425
  };
  
  // Define SVG dimensions and margins
  const width = 800;
  const height = 500;
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  
  // Define node colors
  const nodeColors = {
    "Package Arrival": "#4682B4", // Steel Blue
    "Assignment": "#6495ED", // Cornflower Blue
    "Locker Storage": "#87CEEB", // Sky Blue
    "Amazon": "#FF9900", // Amazon Orange
    "USPS": "#004B87", // USPS Blue
    "UPS": "#351C15", // UPS Brown
    "FedEx": "#4D148C", // FedEx Purple
    "Other Carriers": "#888888", // Gray
    "Delivery/Pickup": "#66BB6A" // Green
  };
  
  // Calculate link colors based on processing time
  const getProcessingTimeColor = (source, target) => {
    // For links from locker storage to carriers
    if (source === 2) {
      const carrierName = data.nodes[target].name;
      const processingTime = processingTimes[carrierName] || processingTimes["Other"];
      
      // Color scale from green (fastest) to red (slowest)
      if (processingTime < 40) return "#66BB6A"; // Green
      if (processingTime < 70) return "#FFA726"; // Orange
      if (processingTime < 100) return "#EF6C00"; // Dark Orange
      return "#D32F2F"; // Red
    }
    
    // Default color for other links
    return "#AAAAAA";
  };
  
  // Generate the Sankey diagram using D3
  React.useEffect(() => {
    const svg = d3.select("#sankey-container");
    svg.selectAll("*").remove();
    
    const nodeMap = {};
    data.nodes.forEach((node, i) => {
      nodeMap[i] = { ...node, index: i };
    });
    
    // Define node positions (manually for better control)
    const nodePositions = [
      { x: 0, y: innerHeight / 2 }, // Package Arrival
      { x: innerWidth / 5, y: innerHeight / 2 }, // Assignment
      { x: (innerWidth * 2) / 5, y: innerHeight / 2 }, // Locker Storage
      { x: (innerWidth * 3) / 5, y: innerHeight / 6 }, // Amazon
      { x: (innerWidth * 3) / 5, y: (innerHeight * 2) / 6 }, // USPS
      { x: (innerWidth * 3) / 5, y: (innerHeight * 3) / 6 }, // UPS
      { x: (innerWidth * 3) / 5, y: (innerHeight * 4) / 6 }, // FedEx
      { x: (innerWidth * 3) / 5, y: (innerHeight * 5) / 6 }, // Other Carriers
      { x: innerWidth, y: innerHeight / 2 } // Delivery/Pickup
    ];
    
    // Calculate node dimensions
    const nodeWidth = 20;
    const getNodeHeight = (node, index) => {
      // For carrier nodes
      if (index >= 3 && index <= 7) {
        const link = data.links.find(l => l.source === 2 && l.target === index);
        return link ? Math.max(20, (link.value / 100)) : 20;
      }
      // For other nodes
      return 200;
    };
    
    // Draw the links
    const linksGroup = svg.append("g")
      .attr("fill", "none")
      .attr("stroke-opacity", 0.5);
    
    data.links.forEach(link => {
      const sourceNode = nodePositions[link.source];
      const targetNode = nodePositions[link.target];
      const sourceHeight = getNodeHeight(nodeMap[link.source], link.source);
      const targetHeight = getNodeHeight(nodeMap[link.target], link.target);
      
      // Calculate link width based on value
      const linkWidth = Math.max(1, link.value / 100);
      
      // Adjust source and target Y positions for carrier nodes
      let sourceY = sourceNode.y;
      let targetY = targetNode.y;
      
      // For links from locker storage to carriers
      if (link.source === 2) {
        // Distribute links vertically
        sourceY = sourceNode.y - sourceHeight/3 + (link.target - 3) * (sourceHeight/6);
      }
      
      // For links from carriers to delivery
      if (link.target === 8) {
        // Distribute links vertically on the delivery node
        targetY = targetNode.y - targetHeight/3 + (link.source - 3) * (targetHeight/10);
      }
      
      // Control points for curved path
      const cp1x = sourceNode.x + (targetNode.x - sourceNode.x) / 3;
      const cp2x = sourceNode.x + 2 * (targetNode.x - sourceNode.x) / 3;
      
      // Draw the link
      linksGroup.append("path")
        .attr("d", `
          M ${sourceNode.x + nodeWidth} ${sourceY}
          C ${cp1x} ${sourceY}, ${cp2x} ${targetY}, ${targetNode.x} ${targetY}
        `)
        .attr("stroke", getProcessingTimeColor(link.source, link.target))
        .attr("stroke-width", linkWidth)
        .attr("fill", "none")
        .append("title")
        .text(`${nodeMap[link.source].name} → ${nodeMap[link.target].name}: ${link.value} packages`);
    });
    
    // Draw the nodes
    const nodesGroup = svg.append("g");
    
    data.nodes.forEach((node, i) => {
      const pos = nodePositions[i];
      const height = getNodeHeight(node, i);
      
      // Draw node rectangle
      nodesGroup.append("rect")
        .attr("x", pos.x)
        .attr("y", pos.y - height/2)
        .attr("width", nodeWidth)
        .attr("height", height)
        .attr("fill", nodeColors[node.name] || "#999")
        .append("title")
        .text(node.name);
      
      // Add node labels
      nodesGroup.append("text")
        .attr("x", i === 8 ? pos.x - 10 : pos.x + nodeWidth + 5) // Adjust for last node
        .attr("y", pos.y)
        .attr("dy", "0.35em")
        .attr("text-anchor", i === 8 ? "end" : "start") // Align right for last node
        .text(node.name)
        .style("font-size", "12px")
        .style("font-weight", "bold");
      
      // Add volume labels for carriers
      if (i >= 3 && i <= 7) {
        const link = data.links.find(l => l.source === 2 && l.target === i);
        if (link) {
          nodesGroup.append("text")
            .attr("x", pos.x + nodeWidth + 5)
            .attr("y", pos.y + 15)
            .attr("text-anchor", "start")
            .text(`${link.value} packages`)
            .style("font-size", "10px");
          
          // Add processing time label
          const processingTime = processingTimes[node.name] || processingTimes["Other"];
          nodesGroup.append("text")
            .attr("x", pos.x + nodeWidth + 5)
            .attr("y", pos.y + 30)
            .attr("text-anchor", "start")
            .text(`${processingTime.toFixed(1)} hours avg.`)
            .style("font-size", "10px")
            .style("fill", processingTime > 100 ? "#D32F2F" : "#000");
        }
      }
    });
    
    // Add legend
    const legend = svg.append("g")
      .attr("transform", `translate(${margin.left}, ${innerHeight + margin.top + 10})`);
    
    legend.append("text")
      .attr("x", 0)
      .attr("y", 0)
      .text("Processing Time:")
      .style("font-weight", "bold")
      .style("font-size", "12px");
    
    const legendItems = [
      { label: "< 40 hours", color: "#66BB6A" },
      { label: "40-70 hours", color: "#FFA726" },
      { label: "70-100 hours", color: "#EF6C00" },
      { label: "> 100 hours", color: "#D32F2F" }
    ];
    
    legendItems.forEach((item, i) => {
      legend.append("rect")
        .attr("x", i * 120)
        .attr("y", 10)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", item.color);
      
      legend.append("text")
        .attr("x", i * 120 + 20)
        .attr("y", 20)
        .text(item.label)
        .style("font-size", "11px");
    });
  }, []);
  
  return (
    <div className="flex flex-col items-center p-4">
      <h2 className="text-xl font-bold mb-2">Package Flow Sankey Diagram</h2>
      <p className="text-sm text-gray-600 mb-4">Visualization of package processing flow and times</p>
      
      <div className="relative w-full overflow-x-auto">
        <svg 
          id="sankey-container" 
          width={width} 
          height={height + 40} 
          className="mx-auto"
        ></svg>
      </div>
      
      <button 
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? "Hide Details" : "Show Additional Details"}
      </button>
      
      {showDetails && (
        <div className="mt-4 w-full max-w-2xl">
          <h3 className="text-lg font-bold mb-2">Locker Bank Utilization</h3>
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(lockerBanks).map(([bank, count]) => (
              <div key={bank} className="bg-gray-100 p-2 rounded">
                <div className="font-bold">{bank}</div>
                <div>{count} packages</div>
                <div className="w-full bg-gray-200 h-2 mt-1">
                  <div 
                    className="bg-blue-500 h-2" 
                    style={{width: `${(count / 1052) * 100}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          
          <h3 className="text-lg font-bold mt-6 mb-2">Carrier Processing Times</h3>
          <div className="grid grid-cols-5 gap-4">
            {Object.entries(processingTimes).map(([carrier, time]) => (
              <div key={carrier} className="bg-gray-100 p-2 rounded">
                <div className="font-bold">{carrier}</div>
                <div>{time.toFixed(1)} hours avg.</div>
                <div className="w-full bg-gray-200 h-2 mt-1">
                  <div 
                    className={`h-2 ${
                      time < 40 ? "bg-green-500" : 
                      time < 70 ? "bg-yellow-500" : 
                      time < 100 ? "bg-orange-500" : "bg-red-500"
                    }`}
                    style={{width: `${Math.min(100, (time / 172.4) * 100)}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h3 className="text-lg font-bold mb-2">Key Insights</h3>
            <ul className="list-disc pl-5 space-y-2">
              <li>Amazon is the most common carrier (3,524 packages)</li>
              <li>Average delivery time varies significantly by carrier (18 to 220+ hours)</li>
              <li>USPS has high volume but longer processing times (103.9 hours avg)</li>
              <li>Locker banks 5, 6, 7, and 8 have the highest utilization</li>
              <li>Amazon packages are processed most efficiently (33.7 hours avg)</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default SankeyDiagram;
