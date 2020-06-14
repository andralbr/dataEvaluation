function resTimeArray = processTime( timeStamps )
  
  resTimeArray = [];

  if length(timeStamps) % 2 ~= 0 
    %return;  
  end
 
  noElements = length( timeStamps ) / 2;
  
  indices = 1:noElements;
  activeElements = true(1,noElements);

  element = [timeStamps(1) timeStamps(2)];
  activeElements(1) = false;
  


  while any(activeElements)
     elementsMerged = false;
    
     for n = indices(activeElements)

        timePair = [timeStamps(2*n-1) timeStamps(2*n)];
      
        if ~(timePair(1) > element(2) || timePair(2) < element(1)) 
          element = [min(element(1),timePair(1)) max(element(2),timePair(2))];
          activeElements(n) = false;
          elementsMerged = true;
          break;  
        end
       
     end
    
     if ~elementsMerged
      resTimeArray = [resTimeArray element];
      
      idx = find( activeElements, true);
      element = [timeStamps(2*idx-1) timeStamps(2*idx)];
     end
       
  end
  
  % Adds last element result vector
  resTimeArray = [resTimeArray element];
  
end
